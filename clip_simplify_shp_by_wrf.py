import xarray as xr
import geopandas as gpd
from shapely.geometry import box
from shapely.ops import transform
import pyproj
import argparse

def get_wrf_bounds(wrfout_path):
    """Obtém os limites geográficos do arquivo wrfout."""
    ds = xr.open_dataset(wrfout_path)
    lats = ds['XLAT'].isel(Time=0)
    lons = ds['XLONG'].isel(Time=0)
    
    min_lon = float(lons.min())
    max_lon = float(lons.max())
    min_lat = float(lats.min())
    max_lat = float(lats.max())
    
    return (min_lon, min_lat, max_lon, max_lat)

def clip_and_simplify_shapefile(shp_path, wrf_bounds, output_path, tolerance=0.01):
    """Corta e simplifica o shapefile de entrada de acordo com os limites do WRF."""
    gdf = gpd.read_file(shp_path)
    
    # Caixa delimitadora do WRF
    min_lon, min_lat, max_lon, max_lat = wrf_bounds
    wrf_box = box(min_lon, min_lat, max_lon, max_lat)
    
    # Faz o recorte
    clipped = gdf[gdf.intersects(wrf_box)].copy()
    clipped['geometry'] = clipped.intersection(wrf_box)
    
    # Reduz a resolução (simplifica a geometria)
    simplified = clipped.copy()
    simplified['geometry'] = simplified['geometry'].simplify(tolerance, preserve_topology=True)

    # Salva o shapefile ou GeoJSON
    if output_path.endswith('.geojson'):
        simplified.to_file(output_path, driver='GeoJSON')
    else:
        simplified.to_file(output_path)
    
    print(f'Salvo em: {output_path}')

def main():
    parser = argparse.ArgumentParser(description="Recorta e simplifica shapefile com base no domínio de um WRFOUT.")
    parser.add_argument("--wrfout", required=True, help="Arquivo wrfout com o domínio.")
    parser.add_argument("--shapefile", required=True, help="Shapefile de entrada.")
    parser.add_argument("--output", default="shp_recortado.shp", help="Shapefile ou GeoJSON de saída.")
    parser.add_argument("--tolerance", type=float, default=0.01, help="Tolerância para simplificação (graus).")
    
    args = parser.parse_args()

    wrf_bounds = get_wrf_bounds(args.wrfout)
    clip_and_simplify_shapefile(args.shapefile, wrf_bounds, args.output, args.tolerance)

if __name__ == "__main__":
    main()

