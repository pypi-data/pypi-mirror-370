import folium
import typing

def MarkCoordinatesOnMap(coordinates:list[typing.Tuple[float, float]], output_html_file:str='map.html'):
    """
    生成一个包含经纬度的世界地图，并保存为 HTML 文件。

    :param coordinates: 一个包含经纬度的列表，格式为 [(lat1, lon1), (lat2, lon2), ...]
    :param output_file: 输出文件名，默认为 'map.html'
    """
    # 创建一个基础地图，中心点为第一个经纬度
    if not coordinates:
        raise ValueError("坐标列表不能为空")
    
    if not output_html_file.endswith('.html'):
        output_html_file = output_html_file + '.html'
    
    first_lat, first_lon = coordinates[0]
    m = folium.Map(location=[first_lat, first_lon], zoom_start=2)

    # 添加标记
    for lat, lon in coordinates:
        folium.Marker([lat, lon]).add_to(m)

    # 保存为 HTML 文件
    m.save(output_html_file)