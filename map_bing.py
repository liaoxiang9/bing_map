# -*- coding: utf-8 -*-
'''
PyQt中高德地图交互操作
'''
import math
import sys

from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton

# 创建一个 application实例
app = QApplication(sys.argv)
win = QWidget()
win.setWindowTitle('高德地图点标记互动通信')
# 创建一个垂直布局器
layout = QVBoxLayout()
win.setLayout(layout)
# 创建一个 QWebEngineView 对象
view = QWebEngineView()
view.setHtml('''
<!doctype html>
<html>

<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="initial-scale=1.0, user-scalable=no, width=device-width">
  <link rel="stylesheet" href="https://a.amap.com/jsapi_demos/static/demo-center/css/demo-center.css" />
  <style>
    html,
    body,
    #container {
      width: 100%;
      height: 100%;
    }
  </style>
  <title>设置地图级别与中心点</title>
</head>

<body>
  <div id="container"></div>

  <div class="input-card" style="width:24rem;background-color:rgba(255,255,255,0.8)">
         <label style='color:grey'>请输入想要设置的地图中心经纬度：经度,纬度</label>
    <div class="input-item">
            <div class="input-item-prepend">
                <span class="input-item-text" >经纬度</span>
            </div>
            <input id='lnglatInput' type="text" value="116.478935,39.997761">            
    </div>
    <div class="input-item">
      <button id="random-center-btn" class="btn" >设置地图中心点 </button>
    </div>
        <h4>地块信息</h4>
     <label style='color:grey'>请输入地块的长度和宽度(单位：米)：</label>
    <div class="input-item">
            <div class="input-item-prepend">
                <span class="input-item-text" >长度</span>
            </div>
            <input id='lengthInput' type="text" value="100">     
      		<div class="input-item-prepend">
                <span class="input-item-text" >宽度</span>
            </div>
            <input id='widthInput' type="text" value="50">    
    </div>
    <div class="input-item">
      <button id="draw-rectangle" class="btn">绘制矩形(打好地块左下角的点)</button>
    </div>
    <div class="input-item">
      <button id="rotate-acw" class="btn">逆时针旋转1度</button>
      <button id="rotate-cw" class="btn">顺时针旋转1度</button>
    </div>
    
    <h4>路径规划</h4>
    <label style='color:grey'>请输入作业幅宽和最小转弯半径(单位：米)：</label>
    <div class="input-item">
            <div class="input-item-prepend">
                <span class="input-item-text" >作业幅宽</span>
            </div>
            <input id='worklenInput' type="text" value="2">     
      		<div class="input-item-prepend">
                <span class="input-item-text" >最小半径</span>
            </div>
            <input id='minradiusInput' type="text" value="1">
    </div>
    
    <label style='color:grey'>请输入入口序号和机具速度(单位：米/秒)：</label>
    <div class="input-item">
            <div class="input-item-prepend">
                <span class="input-item-text" >入口位置</span>
            </div>
            <input id='enterInput' type="text" value="8">     
            <div class="input-item-prepend">
                <span class="input-item-text" >机具速度</span>
            </div>
            <input id='speedInput' type="text" value="500"> 
    </div>
    
    <div class="input-item">
      <button id="enter-position" class="btn">展示/隐藏入口位置</button>
      <button id="tra-planning" class="btn">仿真展示</button>
    </div>
    <div class="input-item">
      <button id="key-point" class="btn">展示/隐藏关键点位</button>
      <button id="delete-all" class="btn">清空数据</button>
    </div>
  </div>

  <script src="https://webapi.amap.com/maps?v=1.4.15&key=您申请的key值"></script>
  <script src="https://a.amap.com/jsapi_demos/static/demo-center/js/demoutils.js"></script>
  <script>
    //初始化地图
    var satellite = new AMap.TileLayer.Satellite();
    var map = new AMap.Map("container", {
      center: [116.478935,39.997761],
      zoom: 16,
      layers:[satellite],
      resizeEnable: true
  });
    //绑定按钮“设置地图中心点”事件，改变地图中心点
    document.querySelector("#random-center-btn").onclick = function() {
      var lnglat = lnglatInput.value.split(',');
      map.setCenter([lnglat[0], lnglat[1]]); //设置地图中心点
      log.info(`当前中心点已设为 ${lnglat[0]},${lnglat[1]}`);
    }   
    //点击地图加点
  var clickHandler = function(e) {
  var marker = new AMap.Marker({
  position: new AMap.LngLat(e.lnglat.getLng(),e.lnglat.getLat()),
  draggable:true
  });
  map.add(marker);
  //点的右键快捷键:
  var contextMenu = new AMap.ContextMenu();//创建右键菜单
  contextMenu.addItem("删除点", function () {map.remove(marker);}, 0);
  contextMenu.addItem("显示坐标", function () {alert(marker.getPosition());}, 1);
  //绑定鼠标右击事件——弹出右键菜单
  marker.on('rightclick', function (e) {contextMenu.open(map, e.lnglat);});
  };
  //绑定地图单击事件:
  map.on('click', clickHandler);
  //以标的点为基准，画矩形
    var basemk = [0,0];
    var degree = 0;
    var deg = 0;
    var gl = lengthInput.value;
    var gw = widthInput.value;
    var lineArr_ = [];
    var edge_markers = [];
    var enter_flag = 1;
    var key_flag = 1;
    var key_points = [];
    
    document.querySelector("#draw-rectangle").onclick = function() {
    // 点击绘制矩形，先将之前的矩形和路径删除
    var polygons = map.getAllOverlays('polygon');
    for (var i = 0; i < polygons.length; i++) {
        map.remove(polygons[i]);
    }
    lineArr_ = [];
    var polylines = map.getAllOverlays('polyline');
    for (var i = 0; i < polylines.length; i++) {
        map.remove(polylines[i]);
    }   
    var markers = map.getAllOverlays('marker');
    basemk = markers[0].getPosition();
    degree = 0;
    gl = lengthInput.value;
    gw = widthInput.value;
    var lnglat1 = basemk.toString().split(',');
    var lnglat2 = basemk.offset(0,gl).toString().split(',');
    var lnglat3 = basemk.offset(gw,gl).toString().split(',');
    var lnglat4 = basemk.offset(gw,0).toString().split(',');                                                     
    var polygonPath = [
     new AMap.LngLat(lnglat1[0],lnglat1[1]),
     new AMap.LngLat(lnglat2[0],lnglat2[1]),
     new AMap.LngLat(lnglat3[0],lnglat3[1]),
     new AMap.LngLat(lnglat4[0],lnglat4[1])
   ];
   var polygon = new AMap.Polygon({
        path: polygonPath,//设置多边形边界路径
        strokeColor: "#FFFF00", //线颜色
        strokeOpacity: 0.2, //线透明度
        strokeWeight: 3,    //线宽
        fillColor: "#1791fc", //填充色
        fillOpacity: 0.35//填充透明度
    });
      map.add(polygon);
      map.remove(markers[0])
    }
    
     //逆时针旋转
     document.querySelector("#rotate-acw").onclick = function() {
     var pgs = map.getAllOverlays('polygon');
     for (var i = 0; i < pgs.length; i++) {
       map.remove(pgs[i])
     }      
       // 逆时针旋转 degree -1
       degree = degree - 1;
       if(degree < 0){
         deg = -degree;
       }
       else{
         deg = 360 - degree;
       }
        gl = lengthInput.value;
       gw = widthInput.value;
       sin_degree = Math.sin(deg * Math.PI / 180);
       cos_degree = Math.cos(deg * Math.PI / 180);
       // 计算四个角的经纬度
       var lnglat1 = basemk.toString().split(',');    
       var lnglat2 = basemk.offset((-1 * sin_degree * gl),(cos_degree * gl)).toString().split(',');
       var lnglat3 = basemk.offset((gw*cos_degree-gl*sin_degree),(gw*sin_degree+gl*cos_degree)).toString().split(',');
	   var lnglat4 = basemk.offset(gw*cos_degree,gw*sin_degree).toString().split(',');
       var polygonPath = [
       new AMap.LngLat(lnglat1[0],lnglat1[1]),
       new AMap.LngLat(lnglat2[0],lnglat2[1]),
       new AMap.LngLat(lnglat3[0],lnglat3[1]),
       new AMap.LngLat(lnglat4[0],lnglat4[1])
       ];
       var polygon = new AMap.Polygon({
        path: polygonPath,//设置多边形边界路径
        strokeColor: "#FFFF00", //线颜色
        strokeOpacity: 0.2, //线透明度
        strokeWeight: 3,    //线宽
        fillColor: "#1791fc", //填充色
        fillOpacity: 0.35//填充透明度
    });
       map.add(polygon);
    }
    
    //顺时针旋转
     document.querySelector("#rotate-cw").onclick = function() {
     var pgs = map.getAllOverlays('polygon');
     for (var i = 0; i < pgs.length; i++) {
       map.remove(pgs[i])
     }      
       // 逆时针旋转 degree -1
       degree = degree + 1;
       if(degree < 0){
         deg = -degree;
       }
       else{
         deg = 360 - degree;
       }
        gl = lengthInput.value;
       gw = widthInput.value;
       sin_degree = Math.sin(deg * Math.PI / 180);
       cos_degree = Math.cos(deg * Math.PI / 180);
       // 计算四个角的经纬度
       var lnglat1 = basemk.toString().split(',');
       var lnglat2 = basemk.offset((-1 * sin_degree * gl),(cos_degree * gl)).toString().split(',');
       var lnglat3 = basemk.offset((gw*cos_degree-gl*sin_degree),(gw*sin_degree+gl*cos_degree)).toString().split(',');
	   var lnglat4 = basemk.offset(gw*cos_degree,gw*sin_degree).toString().split(',');
       var polygonPath = [
       new AMap.LngLat(lnglat1[0],lnglat1[1]),
       new AMap.LngLat(lnglat2[0],lnglat2[1]),
       new AMap.LngLat(lnglat3[0],lnglat3[1]),
       new AMap.LngLat(lnglat4[0],lnglat4[1])
       ];
       var polygon = new AMap.Polygon({
        path: polygonPath,//设置多边形边界路径
        strokeColor: "#FFFF00", //线颜色
        strokeOpacity: 0.2, //线透明度
        strokeWeight: 3,    //线宽
        fillColor: "#1791fc", //填充色
        fillOpacity: 0.35//填充透明度
    });
       map.add(polygon);
    }
    
    document.querySelector("#enter-position").onclick = function() {
    if(enter_flag == 0){
      if(edge_markers.length > 0){
        for(var i = 0; i < edge_markers.length; i++){
            map.remove(edge_markers[i]);}
        edge_markers = [];
      enter_flag = 1}    
    }
      else{    
      gl = lengthInput.value;
      gw = widthInput.value;
      if(degree < 0){
         deg = -degree;
       }
       else{
         deg = 360 - degree;
       }
      sin_degree = Math.sin(deg * Math.PI / 180);
      cos_degree = Math.cos(deg * Math.PI / 180);

      var lnglat1 = basemk.offset(0 * cos_degree - 10 * sin_degree,0 * sin_degree + 10 * cos_degree).toString().split(',');
      var lnglat2 = basemk.offset(0 * cos_degree - (gl-10) * sin_degree,0 * sin_degree + (gl-10) * cos_degree).toString().split(',');
      var lnglat3 = basemk.offset(10 * cos_degree - gl * sin_degree,10 * sin_degree + gl * cos_degree).toString().split(',');
      var lnglat4 = basemk.offset((gw-10) * cos_degree - gl * sin_degree,(gw-10) * sin_degree + gl * cos_degree).toString().split(',');
      var lnglat5 = basemk.offset(gw * cos_degree - (gl-10) * sin_degree,gw * sin_degree + (gl-10) * cos_degree).toString().split(',');
      var lnglat6 = basemk.offset(gw * cos_degree - 10 * sin_degree,gw * sin_degree + 10 * cos_degree).toString().split(',');
      var lnglat7 = basemk.offset((gw-10) * cos_degree - 0 * sin_degree,(gw-10) * sin_degree + 0 * cos_degree).toString().split(',');
      var lnglat8 = basemk.offset(10 * cos_degree - 0 * sin_degree,10 * sin_degree + 0 * cos_degree).toString().split(',');
        
     edge_markers.push(new AMap.Marker({
        position: new AMap.LngLat(lnglat1[0],lnglat1[1]),
        icon: "https://s1.328888.xyz/2022/08/20/BtCmr.jpg",
        offset: new AMap.Pixel(-10, -10),    
        }));        
     edge_markers.push(new AMap.Marker({
        position: new AMap.LngLat(lnglat2[0],lnglat2[1]),
        icon: "https://s1.328888.xyz/2022/08/20/Btkym.jpg",
        offset: new AMap.Pixel(-10, -10),
        }));    
     edge_markers.push(new AMap.Marker({
        position: new AMap.LngLat(lnglat3[0],lnglat3[1]),
        icon: "https://s1.328888.xyz/2022/08/20/Bt1d7.jpg",
        offset: new AMap.Pixel(-10, -10),
        }));
     edge_markers.push(new AMap.Marker({
        position: new AMap.LngLat(lnglat4[0],lnglat4[1]),
        icon: "https://s1.328888.xyz/2022/08/20/Bt9bk.jpg",
        offset: new AMap.Pixel(-10, -10),
        }));
     edge_markers.push(new AMap.Marker({
        position: new AMap.LngLat(lnglat5[0],lnglat5[1]),
        icon: "https://s1.328888.xyz/2022/08/20/BtKgE.jpg",
        offset: new AMap.Pixel(-10, -10),
        }));
     edge_markers.push(new AMap.Marker({
        position: new AMap.LngLat(lnglat6[0],lnglat6[1]),
        icon: "https://s1.328888.xyz/2022/08/20/BtcnJ.jpg",
        offset: new AMap.Pixel(-10, -10),
        }));
     edge_markers.push(new AMap.Marker({
        position: new AMap.LngLat(lnglat7[0],lnglat7[1]),
        icon: "https://s1.328888.xyz/2022/08/20/Bt24w.jpg",
        offset: new AMap.Pixel(-10, -10),
        }));
     edge_markers.push(new AMap.Marker({
        position: new AMap.LngLat(lnglat8[0],lnglat8[1]),
        icon: "https://s1.328888.xyz/2022/08/20/BtI2i.jpg",
        offset: new AMap.Pixel(-10, -10),
        size: new AMap.Size(10, 10),
        }));        
     for(var i = 0; i < edge_markers.length; i++){
            map.add(edge_markers[i]);
        }
        enter_flag = 0;
      }
    }
    
    var kt = [];
    document.querySelector("#key-point").onclick = function() {
    if(key_flag == 0){
      if(kt.length > 0){
        for(var i = 0; i < kt.length; i++){
            map.remove(kt[i]);}
      key_flag = 1}    
    }
      else{
      if(degree < 0){
         deg = -degree;
       }
       else{
         deg = 360 - degree;
       }
    gl = lengthInput.value;
    gw = widthInput.value;
    sin_degree = Math.sin(deg * Math.PI / 180);
    cos_degree = Math.cos(deg * Math.PI / 180);
    for(var i = 0; i < key_points.length; i++){
        var x = key_points[i][0];
        var y = key_points[i][1];
        var x_new = x * cos_degree - y * sin_degree;
        var y_new = x * sin_degree + y * cos_degree;
        var lnglat = basemk.offset(x_new,y_new).toString().split(',');
        var marker = new AMap.Marker({
  position: new AMap.LngLat(lnglat[0],lnglat[1]),
  draggable:true
  });
  map.add(marker);
  kt.push(marker);
  //点的右键快捷键:
  var contextMenu = new AMap.ContextMenu();//创建右键菜单
  contextMenu.addItem("删除点", function () {map.remove(marker);}, 0);
  contextMenu.addItem("显示坐标", function () {alert(marker.getPosition());}, 1);
  //绑定鼠标右击事件——弹出右键菜单
  marker.on('rightclick', function (e) {contextMenu.open(map, e.lnglat);});
  };
        key_flag = 0;
    }
      }
    
    
    var getdata = function() {          
    return [gl,gw,worklenInput.value,minradiusInput.value,enterInput.value];
    }
     var savekp = function(kp) {          
    key_points = kp;
    }
    
    var drawline = function(points){
      lineArr_ = [];
    var deletelines = map.getAllOverlays('polyline');
    for (var i = 0; i < deletelines.length; i++) {
        map.remove(deletelines[i]);
    }   
    if(degree < 0){
         deg = -degree;
       }
       else{
         deg = 360 - degree;
       }
    gl = lengthInput.value;
    gw = widthInput.value;
    sin_degree = Math.sin(deg * Math.PI / 180);
    cos_degree = Math.cos(deg * Math.PI / 180);
    for(var i = 0; i < points.length; i++){
        var x = points[i][0];
        var y = points[i][1];
        var x_new = x * cos_degree - y * sin_degree;
        var y_new = x * sin_degree + y * cos_degree;
        var lnglat = basemk.offset(x_new,y_new).toString().split(',');
        lineArr_.push(new AMap.LngLat(lnglat[0],lnglat[1]));
    }
    var polyline = new AMap.Polyline({
        map: map,
        path: lineArr_,
        showDir:true,
        strokeColor: "#FF0000",  //线颜色
        strokeOpacity: 1,     //线透明度
        strokeWeight: 1,      //线宽
        // strokeStyle: "solid"  //线样式
    });
    }
    
    document.querySelector("#tra-planning").onclick = function() {
      var markers = map.getAllOverlays('marker');
    for (var i = 0; i < markers.length; i++) {
        map.remove(markers[i]);
    } 
        marker = new AMap.Marker({
            map: map,
            position: basemk,
            icon: "https://webapi.amap.com/images/car.png",
            offset: new AMap.Pixel(-26, -13),
            autoRotation: true,
            angle:-90,
        });       
        var passedPolyline = new AMap.Polyline({
            map: map,
            // path: lineArr,
            strokeColor: "#00FF00",  //线颜色
            // strokeOpacity: 1,     //线透明度
            strokeWeight: 1,      //线宽
            // strokeStyle: "solid"  //线样式
        });        
        marker.on('moving', function (e) {
        passedPolyline.setPath(e.passedPath);
        });        
        map.setFitView();
        marker.moveAlong(lineArr_, speedInput.value);       
    }
    
    document.querySelector("#delete-all").onclick = function() {
    // 清除所有数据
    var polygons = map.getAllOverlays('polygon');
    for (var i = 0; i < polygons.length; i++) {
        map.remove(polygons[i]);
    }
    var polylines = map.getAllOverlays('polyline');
    for (var i = 0; i < polylines.length; i++) {
        map.remove(polylines[i]);
    }   
    var markers = map.getAllOverlays('marker');
     for (var i = 0; i < markers.length; i++) {
        map.remove(markers[i]);
    }       
    basemk = [0,0];
    degree = 0;
    deg = 0;
    gl = lengthInput.value;
    gw = widthInput.value;
    lineArr_ = [];
    edge_markers = [];
    enter_flag = 1;
    key_flag = 1;
    key_points = [];
    kt = [];
    }
  </script>
</body>

</html>
''')
# 创建一个按钮去调用 JavaScript代码
button = QPushButton('路径规划')


def tra_planning(grd_l, grd_w, w, r, enter):
    if w == 2 * r:
        return semicircle_turn(grd_l, grd_w, w, r, enter)
    elif w > 2 * r:
        return bow_turn(grd_l, grd_w, w, r, enter)
    else:
        return pear_turn(grd_l, grd_w, w, r, enter)


def semicircle_turn(grd_l, grd_w, w, r, enter):
    if enter in [1, 2, 5, 6]:
        grd_w, grd_l = grd_l, grd_w
    turn_time = int(grd_w / w)
    l_free = (grd_w - turn_time * w) / 2
    tra_point = [[l_free + w / 2, 0], [l_free + w / 2, r]]
    key_point = [[l_free + w / 2, 0]]
    flag = 1
    for i in range(turn_time - 1):
        if flag:
            a, b = l_free + w * (i + 1), grd_l - r
            m = (2 * math.pi) / 60
            for j in range(31):
                x = a + r * math.sin(-math.pi / 2 + m * j)
                y = b + r * math.cos(-math.pi / 2 + m * j)
                tra_point.append([x, y])
                if j == 0:
                    key_point.append([x, y])
        else:
            a, b = l_free + w * (i + 1), r
            m = (2 * math.pi) / 60
            for j in range(31):
                x = a + r * math.sin(-math.pi / 2 - m * j)
                y = b + r * math.cos(-math.pi / 2 - m * j)
                tra_point.append([x, y])
                if j == 0:
                    key_point.append([x, y])
        flag = 1 - flag
    if turn_time % 2 == 0:
        tra_point.extend([[grd_w - l_free - w / 2, r], [grd_w - l_free - w / 2, 0]])
        key_point.append([grd_w - l_free - w / 2, 0])
    else:
        tra_point.extend([[grd_w - l_free - w / 2, grd_l - r], [grd_w - l_free - w / 2, grd_l]])
        key_point.append([grd_w - l_free - w / 2, grd_l])
    return tra_revised(tra_point, grd_l, grd_w, enter), tra_revised(key_point, grd_l, grd_w, enter)


def pear_turn(grd_l, grd_w, w, r, enter):
    if enter in [1, 2, 5, 6]:
        grd_w, grd_l = grd_l, grd_w
    turn_time = int(grd_w / w)
    l_free = (grd_w - turn_time * w) / 2
    tra_point = [[l_free + w / 2, 0], [l_free + w / 2, r]]
    key_point = [[l_free + w / 2, 0]]
    flag = 1
    for i in range(turn_time - 1):
        part_point = []
        if flag:
            a, b = l_free + w * (i + 1 / 2) - r, grd_l - r - math.sqrt(4 * r ** 2 - (r + w / 2) ** 2)
            m = math.acos((w / 2 + r) / (2 * r)) / 15
            for j in range(16):
                x = a + r * math.sin(math.pi / 2 - m * j)
                y = b + r * math.cos(math.pi / 2 - m * j)
                part_point.append([x, y])
                if j == 0:
                    key_point.append([x, y])
            for j in range(15):
                part_point.append(
                    [2 * part_point[15][0] - part_point[14 - j][0], 2 * part_point[15][1] - part_point[14 - j][1]])
            tra_point.extend(part_point)

            a, b = l_free + w * (i + 1), grd_l - r
            m = (2 * math.pi) / 60
            for j in range(1, 30):
                x = a + r * math.sin(-math.pi / 2 + m * j)
                y = b + r * math.cos(-math.pi / 2 + m * j)
                tra_point.append([x, y])

            for j in range(31):
                tra_point.append(
                    [2 * (l_free + w * (i + 1)) - part_point[30 - j][0], part_point[30 - j][1]])

        else:
            a, b = l_free + w * (i + 1 / 2) - r, r + math.sqrt(4 * r ** 2 - (r + w / 2) ** 2)
            m = math.acos((w / 2 + r) / (2 * r)) / 15
            for j in range(16):
                x = a + r * math.sin(math.pi / 2 + m * j)
                y = b + r * math.cos(math.pi / 2 + m * j)
                part_point.append([x, y])
                if j == 0:
                    key_point.append([x, y])
            for j in range(15):
                part_point.append(
                    [2 * part_point[15][0] - part_point[14 - j][0], 2 * part_point[15][1] - part_point[14 - j][1]])
            tra_point.extend(part_point)

            a, b = l_free + w * (i + 1), r
            m = (2 * math.pi) / 60
            for j in range(1, 30):
                x = a + r * math.sin(-math.pi / 2 - m * j)
                y = b + r * math.cos(-math.pi / 2 - m * j)
                tra_point.append([x, y])

            for j in range(31):
                tra_point.append(
                    [2 * (l_free + w * (i + 1)) - part_point[30 - j][0], part_point[30 - j][1]])
        flag = 1 - flag

    if turn_time % 2 == 0:
        tra_point.extend([[grd_w - l_free - w / 2, r], [grd_w - l_free - w / 2, 0]])
        key_point.append([grd_w - l_free - w / 2, 0])
    else:
        tra_point.extend([[grd_w - l_free - w / 2, grd_l - r], [grd_w - l_free - w / 2, grd_l]])
        key_point.append([grd_w - l_free - w / 2, grd_l])
    return tra_revised(tra_point, grd_l, grd_w, enter), tra_revised(key_point, grd_l, grd_w, enter)


def bow_turn(grd_l, grd_w, w, r, enter):
    if enter in [1, 2, 5, 6]:
        grd_w, grd_l = grd_l, grd_w
    turn_time = int(grd_w / w)
    l_free = (grd_w - turn_time * w) / 2
    tra_point = [[l_free + w / 2, 0], [l_free + w / 2, r]]
    key_point = [[l_free + w / 2, 0], [l_free + w / 2, r]]
    flag = 1
    for i in range(turn_time - 1):
        if flag:
            a, b = l_free + w * (i + 1 / 2) + r, grd_l - r
            m = (2 * math.pi) / 60
            for j in range(16):
                x = a + r * math.sin(-math.pi / 2 + m * j)
                y = b + r * math.cos(-math.pi / 2 + m * j)
                tra_point.append([x, y])
                if j == 0:
                    key_point.append([x, y])

            a, b = l_free + w * (i + 3 / 2) - r, grd_l - r
            m = (2 * math.pi) / 60
            for j in range(16):
                x = a + r * math.sin(0 + m * j)
                y = b + r * math.cos(0 + m * j)
                tra_point.append([x, y])
        else:
            a, b = l_free + w * (i + 1 / 2) + r, r
            m = (2 * math.pi) / 60
            for j in range(16):
                x = a + r * math.sin(-math.pi / 2 - m * j)
                y = b + r * math.cos(-math.pi / 2 - m * j)
                tra_point.append([x, y])
                if j == 0:
                    key_point.append([x, y])

            a, b = l_free + w * (i + 3 / 2) - r, r
            m = (2 * math.pi) / 60
            for j in range(16):
                x = a + r * math.sin(-math.pi - m * j)
                y = b + r * math.cos(-math.pi - m * j)
                tra_point.append([x, y])
        flag = 1 - flag
    if turn_time % 2 == 0:
        tra_point.extend([[grd_w - l_free - w / 2, r], [grd_w - l_free - w / 2, 0]])
        key_point.append([grd_w - l_free - w / 2, 0])
    else:
        tra_point.extend([[grd_w - l_free - w / 2, grd_l - r], [grd_w - l_free - w / 2, grd_l]])
        key_point.append([grd_w - l_free - w / 2, grd_l])
    return tra_revised(tra_point, grd_l, grd_w, enter), tra_revised(key_point, grd_l, grd_w, enter)


def tra_revised(tra, grd_l, grd_w, enter):
    if enter == 7:
        for point in tra:
            point[0], point[1] = round(grd_w - point[0], 2), round(point[1], 2)
    elif enter == 3:
        for point in tra:
            point[0], point[1] = round(point[0], 2), round(grd_l - point[1], 2)
    elif enter == 4:
        for point in tra:
            point[0], point[1] = round(grd_w - point[0], 2), round(grd_l - point[1], 2)
    elif enter == 1:
        for point in tra:
            point[0], point[1] = round(point[1], 2), round(point[0], 2)
    elif enter == 2:
        for point in tra:
            point[0], point[1] = round(point[1], 2), round(grd_w - point[0], 2)
    elif enter == 6:
        for point in tra:
            point[0], point[1] = round(grd_l - point[1], 2), round(point[0], 2)
    elif enter == 5:
        for point in tra:
            point[0], point[1] = round(grd_l - point[1], 2), round(grd_w - point[0], 2)
    return tra


def js_callback(result):
    points, kp = tra_planning(float(result[0]), float(result[1]), float(result[2]), float(result[3]), int(result[4]))
    print(points)
    view.page().runJavaScript("drawline({})".format(points))  # 这里将点列传入javascript
    view.page().runJavaScript("savekp({})".format(kp))


def complete_name():
    view.page().runJavaScript('getdata();', js_callback)


button.clicked.connect(complete_name)

# 把QWebView和button加载到layout布局中
layout.addWidget(view)
layout.addWidget(button)

# 显示窗口和运行app
win.show()
sys.exit(app.exec_())
