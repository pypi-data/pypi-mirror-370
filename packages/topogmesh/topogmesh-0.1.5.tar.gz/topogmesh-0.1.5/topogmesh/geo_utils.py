import tempfile
from osgeo import gdal, osr
from yirgacheffe.layers import RasterLayer
import yirgacheffe as yg

def to_utm(input_raster: RasterLayer) -> RasterLayer:
    with tempfile.NamedTemporaryFile(suffix='.tif', delete=True) as tmpfile:
        input_raster.to_geotiff(tmpfile.name)
        ds = gdal.Open(tmpfile.name)
    gt = ds.GetGeoTransform()
    x_center = gt[0] + (ds.RasterXSize * gt[1]) / 2
    y_center = gt[3] + (ds.RasterYSize * gt[5]) / 2

    utm_zone = int((x_center + 180) / 6) + 1
    hemisphere = 'north' if y_center >= 0 else 'south'

    srs = osr.SpatialReference()
    srs.SetUTM(utm_zone, hemisphere == 'north')
    srs.SetWellKnownGeogCS("WGS84")

    dst_wkt = srs.ExportToWkt()

    with tempfile.NamedTemporaryFile(suffix='.tif', delete=True) as tmpfile:
        gdal.Warp(
            tmpfile.name,
            ds,
            dstSRS=dst_wkt,
            format="GTiff"
        )

        warped_raster = yg.read_raster(tmpfile.name)

    return warped_raster