# 校园动态导航系统

数据结构课程大作业项目，后端基于 FastAPI，提供校园最短路径导航接口；前端基于 Vue，用于演示固定场景下的校园导航效果。

## 项目结构

```text
project/
├── app/                    # 后端业务代码
│   ├── algorithm/          # Dijkstra / Floyd 算法
│   ├── api/                # FastAPI 路由
│   ├── data/               # 校园图数据
│   ├── graph/              # 图结构定义
│   ├── models/             # 请求/响应模型
│   └── services/           # 导航服务
├── frontend/               # Vue 前端演示页面
├── main.py                 # 后端启动入口
├── requirements.txt        # 后端依赖
└── tests.py                # 接口测试脚本
```

## 后端说明

后端提供两套最短路径接口，请求参数和返回结构一致，唯一区别是底层算法不同：

- `POST /api/navigation`
  - 使用 Dijkstra 算法
- `POST /api/navigation/floyd`
  - 使用 Floyd 算法

### 请求参数

```json
{
  "start": 35,
  "end": 22,
  "mode": "walk",
  "period": "normal",
  "strategy": "distance"
}
```

字段说明：

- `start` / `end`：起点、终点节点编号
- `mode`：出行方式
  - `walk`
  - `bike`
- `period`：时段模式
  - `normal`
  - `morning_peak`
  - `lunch_peak`
  - `evening_peak`
- `strategy`：路径策略
  - `distance`
  - `time`

### 响应示例

```json
{
  "path": [35, 9, 18, 22],
  "path_names": ["桃蹊饭堂", "学思苑I", "至善楼", "格致楼"],
  "distance": 185.0,
  "time": 132.14
}
```

### 启动后端

1、在项目根目录建立文件
```
.env
```

2、添加下面字段，并写入自己的api key
DEEPSEEK_API_KEY={此处连同花括号一起替换为你自己的apikey}

在项目根目录执行：

```bash
pip install -r requirements.txt
python main.py
```

默认地址：

`http://127.0.0.1:8000`

健康检查接口：

`GET /health`

## 前端说明

前端目录固定为：

`project/frontend`

前端为 Vue + Vite 演示页面，整体风格参考现代地图导航应用。  
其中：

- 文字导航、距离、耗时、JSON 返回内容来自后端真实接口
- 地图路线展示为预绘制示例图，仅用于图像导航演示
- 不在前端重复实现真实路径规划算法

### 固定演示场景

- 起点：`桃蹊饭堂（C2）`
- 终点：`格致楼（S1）`

### 前端支持的演示维度

出行方式：

- 步行
- 自行车

时段模式：

- 普通时段
- 早高峰时段

### 前端展示内容

- 校园地图展示区域
- 示例路线可视化展示
- 出行方式切换
- 时段切换
- 导航结果面板
- 接口返回 JSON
- 接口响应时间
- 逐步文字导航说明

### 启动前端

先启动后端，再进入前端目录执行：

```bash
cd frontend
npm install
npm run dev
```

默认前端地址：

`http://127.0.0.1:5173`

## 演示资源说明

- 学校地图图片
- 已用红色路线标注好的示例导航路径图片

这些资源已复制到前端静态目录下使用：

- `frontend/public/assets/maps/`
- `frontend/public/assets/routes/`

## 测试说明

项目根目录下提供了接口测试脚本：

```bash
python tests.py
```

当前测试脚本会输出：

- 接口状态码
- 请求到响应的耗时
- 返回的完整 JSON
- Dijkstra 与 Floyd 结果对比

## 说明

本项目中：

- 后端导航接口支持完整的文字导航服务
- 前端图像导航仅实现示例演示功能,文字导航功能正常
- Floyd 接口作为与 Dijkstra 平行的第二套算法接口
