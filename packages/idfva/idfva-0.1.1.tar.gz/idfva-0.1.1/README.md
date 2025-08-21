# Welcome to idfva

|        |        |
|--------|--------|
| Package | [![Latest PyPI Version](https://img.shields.io/pypi/v/idfva.svg)](https://pypi.org/project/idfva/) [![Supported Python Versions](https://img.shields.io/pypi/pyversions/idfva.svg)](https://pypi.org/project/idfva/) [![Documentation](https://readthedocs.org/projects/idfva/badge/?version=latest)](https://idfva.readthedocs.io/en/latest/?badge=latest) |
| Meta   | [![Code of Conduct](https://img.shields.io/badge/Contributor%20Covenant-v2.0%20adopted-ff69b4.svg)](CODE_OF_CONDUCT.md) |

*TODO: the above badges that indicate python version and package version will only work if your package is on PyPI.
If you don't plan to publish to PyPI, you can remove them.*

The idfva (IncrementalDebrisFlowVolumeAnalyzer) is a Python tool for estimating intra-channel volume of erosion and deposition along a flow path. The series of semi-automated scripts which make up IncrementalDebrisFlowVolumeAnalyzer can be looped using a master text file and/or the glob package depending on the user file structure, to efficiently run volume estimations across an area of interest. The IncrementalDebrisFlowVolumeAnalyzer relies heavily on the Fiona, Rasterio, and Shapely packages for reading and writing geospatial data.

This tool was designed to be used by geohazard and geomorphology researchers in tandem with external data, field work, and geomorphometric analyses. Students may also use this tool to gain familiarity with debris flow hazards, change detection data types, and geospatial data manipulationin Python with hands-on application to real world problems.

## Get started

You can install this package into your preferred Python environment using pip:

```bash
$ pip install idfva
```

To use idfva in your code:

```python
"""
Example workflow for end-to-end idfva use.
"""

# --- 1. Convert LAS to Raster ---
import las2ras
las_file = "C:/Users/path/to/input/las.las"
scalar_field = "M3C2 distance"
output_raster = "C:/Users/path/to/output/raster.tif"
cell_size = 1
method = 'linear'
las2ras.print_scalar_field(las_file, scalar_field, num_values=10)
las2ras.las_to_raster(las_file, scalar_field, output_raster, cell_size, method)

# --- 2. Process Watersheds (DEM hydrology) ---
import process_watersheds
dem_path = "C:/Users/path/to/DEM.tif"
fdir_output_file = "C:/Users/path/to/flow/direction.tif"
acc_output_file = "C:/Users/path/to/flow/accumulation.tif"
crs_str = "+proj=utm +zone=13 +ellps=GRS80 +units=m +no_defs"

grid, dem = process_watersheds.read_dem(dem_path)
inflated_dem = process_watersheds.condition_dem(grid, dem)
fdir_d8 = process_watersheds.compute_flow_direction(grid, inflated_dem)
acc_d8 = process_watersheds.compute_flow_accumulation(grid, fdir_d8)
process_watersheds.save_raster(fdir_d8, fdir_output_file, crs_str, grid.affine)
process_watersheds.save_raster(acc_d8, acc_output_file, crs_str, grid.affine)
process_watersheds.plot_array(acc_d8, grid, "Flow Accumulation", "cubehelix", "Upstream Cells", log_norm=True)
process_watersheds.plot_array(fdir_d8, grid, "Flow Direction", "viridis", "Flow Direction")

# --- 3. Generate Query Points Along Path ---
import generate_query_points
accumulation_path = acc_output_file
direction_path = fdir_output_file
debris_flow_path = "C:/Users/path/to/flowpath.shp"
output_shapefile_path = "C:/Users/path/to/querypoints.shp"

max_point = generate_query_points.find_max_value_point(debris_flow_path, accumulation_path)
if max_point:
    X, Y = max_point
    x = X[0]
    y = Y[0]
    grid, acc, fdir = generate_query_points.initialize_grid(direction_path, accumulation_path)
    dist, x_snap, y_snap = generate_query_points.calculate_distance_to_outlet(grid, acc, fdir, x, y)
    lon, lat = generate_query_points.convert_coordinates(direction_path, x_snap, y_snap)
    all_points, distances, catchments = generate_query_points.interpolate_points_along_polyline(
        debris_flow_path, direction_path, accumulation_path, dist)
    generate_query_points.save_points_to_shapefile(output_shapefile_path, all_points, distances, catchments)
    generate_query_points.plot_flow_distance(grid, dist, all_points, debris_flow_path)

# --- 4. Prepare Path (dissolve and buffer) ---
import prepare_path
buffered_path = "C:/Users/path/to/buffered/polygon.shp"
buffer_width = 30.0
original_geometries, buffer, crs = prepare_path.create_dissolved_buffer(debris_flow_path, buffered_path, buffer_width)
prepare_path.plot_shapefiles(original_geometries, buffer, crs)

# --- 5. Apply Modified Voronoi ---
import apply_modified_voronoi
investigation_polygons_shapefile = "C:/Users/path/to/investigation/polygons.shp"
buffer_distance = 0

points = apply_modified_voronoi.read_points_from_shapefile(output_shapefile_path)
points_array = np.array([[p.x, p.y] for p in points])
x_min, y_min = points_array.min(axis=0)
x_max, y_max = points_array.max(axis=0)
extra_points = [
    apply_modified_voronoi.Point(x_min - buffer_distance, y_min - buffer_distance),
    apply_modified_voronoi.Point(x_min - buffer_distance, y_max + buffer_distance),
    apply_modified_voronoi.Point(x_max + buffer_distance, y_min - buffer_distance),
    apply_modified_voronoi.Point(x_max + buffer_distance, y_max + buffer_distance)
]
points.extend(extra_points)

with fiona.open(buffered_path, 'r') as src:
    original_polygon = apply_modified_voronoi.unary_union([apply_modified_voronoi.Polygon(feat['geometry']['coordinates'][0]) for feat in src])
clipped_voronoi_polygons = apply_modified_voronoi.compute_voronoi_polygons(points, original_polygon, buffer_distance)
apply_modified_voronoi.save_voronoi_polygons_to_shapefile(clipped_voronoi_polygons, investigation_polygons_shapefile)
apply_modified_voronoi.plot_voronoi_on_map(points, extra_points, clipped_voronoi_polygons, debris_flow_path)
apply_modified_voronoi.plot_voronoi_polygon_areas(clipped_voronoi_polygons)
apply_modified_voronoi.voronoi_polygon_qc(investigation_polygons_shapefile)

# --- 6. Estimate Volumes and Plot ---
import estimate_volume_and_plot
raster_path = output_raster  # or your change detection raster
LoD = 0.25  # User-defined detection limit
polygon_ids = ['803', '830', '766']  # Example tributary IDs

estimate_volume_and_plot.extract_raster_values(raster_path, investigation_polygons_shapefile, debris_flow_path, LoD)
estimate_volume_and_plot.plot_polygons(investigation_polygons_shapefile, 'dep_vol', cmap='Blues')
estimate_volume_and_plot.plot_polygons(investigation_polygons_shapefile, 'ero_vol', cmap='Reds_r')
estimate_volume_and_plot.plot_polygons(investigation_polygons_shapefile, 'net_mob', cmap='Purples_r')
estimate_volume_and_plot.plot_attributes_vs_distance_bar(investigation_polygons_shapefile)
estimate_volume_and_plot.plot_YR_vs_distance(investigation_polygons_shapefile)
estimate_volume_and_plot.plot_YR_vs_catchment(investigation_polygons_shapefile)
estimate_volume_and_plot.plot_attributes_vs_catchment_bar(investigation_polygons_shapefile)
estimate_volume_and_plot.plot_attributes_vs_catchment_log_bar(investigation_polygons_shapefile)
estimate_volume_and_plot.plot_cumulative_vs_distance(investigation_polygons_shapefile)
estimate_volume_and_plot.plot_cumulative_vs_catchment(investigation_polygons_shapefile)
estimate_volume_and_plot.plot_cumulative_vs_distance_scatter(investigation_polygons_shapefile)
estimate_volume_and_plot.plot_cumulative_vs_catchment_scatter(investigation_polygons_shapefile)
```

## Copyright

- Copyright © 2025 Lauren Guido.
- Free software distributed under the [MIT License](./LICENSE).
