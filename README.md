# GitStudy-AngelBand

Support for Git teaching

## AngelBand —— 西部舞台上的乐团

一个用于**版本控制教学**的音乐小游戏：每提交一个新版本，舞台上就多一位乐手。每位乐手控制一条音轨，可以单独开关；几位同时开演，就凑成一支完整的乐队。

当前版本 **v2.6.0**，舞台上有四位乐手：

| 角色 | 位置 | 音轨 | 演出动作 |
| ---- | ---- | ---- | -------- |
| 白发鼓手 | 台上最左 | `drums.mp3` | 四拍一循环：鼓自己蓄力跳起来砸她脑袋，每砸一次换一张随机表情 |
| 唱片小车 | 台上左中 | `singer.mp3` | `Special` 循环，车身随拍轻微呼吸、微摆 |
| 红发吉他手 | 台中央 | `guitar.mp3` | `Relax` 抱琴，叠加右手扫弦与四指拨弦 |
| 蓝发吹号者 | 台上右侧 | `bass.mp3` | `Relax` 站姿，嘴边浮着萨克斯，按拍送气起伏 |

四人各自独立：点一下变彩色并开演，再点变灰退场；同时开演时音轨会自动对齐到同一时刻。底部进度条可以拖动跳转，跳转后拨弦相位会重新对拍。

### 关于那支萨克斯

蓝发吹号者的骨架里自带四支号（小号、单簧管、长号、萨克斯），平时全部隐藏，需要外部挂上。贝斯声部选了**萨克斯**：它是四支里音域最低的、和贝斯声部对得上，轮廓也最优雅。

她没有让号进入骨骼层级，而是用一块独立的精灵钉在 `F_Mouth_I`（嘴部骨骼）上——因为这个角色原本的设定就是"身边浮着乐器"，让号悬在嘴边反而更像她的风格。每拍再做一点送气起伏。

### 关于那只借来的鼓

白发小女孩的骨架里没有乐器，鼓是从另一位和风太鼓角色的图集里**单独裁出来**的（原图 170×170 的一块 `F_Weapon_4`），裁成 `drum.png`，在页面里作为独立精灵跟着她的身体走，不进入骨骼层级。

打法故意做得不讲道理：鼓不是她去敲的，而是**鼓自己蓄力、自己飞过来砸她**。她往哪边歪头都没用，因为鼓的落点每帧取的都是她"此刻"的头部世界坐标——追着砸。节拍对齐到每小节第 3 拍，砸中瞬间她整个头往后一仰、尾巴乱甩，然后换一张随机表情（8 张脸随机，且刻意避开上一张，免得连着两次撞出同款）。

因为动画本身带表情时间线、每帧都会把脸改回去，代码在解析骨骼数据时先把 `F_Face1` / `F_EMO1` 两个槽的 `AttachmentTimeline` 摘掉，之后才由脚本接管表情。

### 上场不"啪"一下

四条音轨都是从乐句中间插进来的，硬起硬停会很跳。所以每位乐手的音量都走一条 smoothstep 包络：

| 场景 | 时长 | 曲线 |
| ---- | ---- | ---- |
| 单人加入合奏 | 0.5s | 0 → 标称音量 |
| 暂停后继续 | 0.28s | 0 → 标称音量 |
| 退场 / 暂停 | 0.3s | 标称音量 → 0，淡完才真正暂停 |

实现上直接逐帧改 `HTMLMediaElement.volume`，搭主循环的便车，不另起定时器。曲线用 smoothstep（两头软、中间快）而不是线性——线性淡入在开头那一下还是听得出来，smoothstep 的起始斜率是 0，才真的"从无到有"。

有个连带改动：退场既然要先淡 0.3 秒再停，"停下的位置"就必须在**淡出结束那一刻**才记进 `pendingPos`，否则会比实际停下的点早 0.3 秒。

### 背景是一块画出来的幕布

远处的落日、层叠台地、火烧云不是矢量的，是一张 AI 生成的画布画（`art/backdrop.png`），铺在最底层；酒馆、木台、灯柱、仙人掌这些需要和角色咬合的物件仍然是 SVG。为了不让绘画抢戏，画布被压暗、去饱和、加了 1px 虚焦推到远处，上面再压一层紫调渐变（`#skyTint`）把颜色拉回原来的紫红夕照；地面层则从顶端透明渐变到近处近乎全黑，让画布里的荒原透出来又不影响木台的对比度。

生成用的提示词：

> Wide panoramic matte painting of a Wild West desert at dusk, designed as a hand-painted theater backdrop. A huge low sun sits in the right third of the frame, half sunk behind a distant mesa. Layered sandstone buttes and flat-topped mesas recede into atmospheric haze along a horizon line at about 60% of the image height, each layer paler and bluer with distance. Dramatic streaked clouds in deep plum, magenta and burnt orange, catching warm rim light from the sunset; a few birds circling high in the sky. The lower third is a dark desert plain fading almost to silhouette, empty and uncluttered, with sparse dry brush. Painterly hand-painted backdrop feel, soft airbrushed gradients, matte finish, rich saturated dusk palette (deep purple #1a0b20, plum #4a1638, burnt sienna #b54a2c, amber #e08a3c, warm highlight #ffd9a0). No text, no lettering, no people, no animals, no buildings, no watermark.

（生成结果右下角带水印，导入时把底部裁掉了 82px；正好那块区域本来也被地面层盖住。）

### 手机上的舞台

舞台是按 1600×900 的宽幅画的，四个人横排站开——这个比例天生和手机的竖屏八字不合。所以两套排法：

| 方向 | 缩放方式 | 结果 |
| ---- | -------- | ---- |
| 横屏 | `cover`（取 `max`） | 铺满整屏，两侧多余部分裁掉，人最大 |
| 竖屏 | `contain`（取 `min`） | 整支乐队按宽度缩进去，脚踩在播放条上方，上方留出天空 |

竖屏时舞台只占下面一条，于是冒出一个新问题：SVG 里那层压暗天空的紫色渐变（`#skyTint`）原本是给整屏铺的，一旦只铺下半截，它的上边缘就会在画布上切出一道**硬缝**。解决办法是给 SVG 挂一层 `mask-image`，从天空顶端到地平线渐隐到透明，让底下的画布天空接管上半屏——缝就没了，人也还站在原来的木台上。

竖屏实在不是这个舞台的主场，所以第一次拉开帷幕时会劝一句「横屏更好看」。这张卡片不会堵门：点「仍然竖屏」、点卡片外面、或者干等 6.5 秒，它自己就让路，之后不再出现。

其它为手机做的调整：

- `100dvh` + `overflow: hidden`，躲开 iOS 地址栏伸缩带来的抖动
- 播放条 `bottom: max(10px, env(safe-area-inset-bottom))`，不压 Home 指示条
- 小屏（`max-width: 560px` / `max-height: 480px`）时按钮缩到 34px、版本号从右下角挪到左上角——原来那个位置正好被播放条盖住
- 渲染分辨率上限：手机上 `devicePixelRatio` 封在 1.5，桌面封在 2；再高就是拿电换像素
- 帷幕、进度条都开了 `touch-action: none` / `manipulation`，拖动不会连带滚页面

## 怎么玩

1. 打开 `index.html`（或部署到 GitHub Pages 在线玩）—— 先看到一块红丝绒帷幕
2. **按住左右拖动**把它拉开（点一下也行），舞台才露出来
3. 点击台上的乐手，开关他/她的音轨；或者按右下角的 **「全部开演」** 一键全员上场（再点变成「全部停演」）
4. 拖动底部进度条跳到任意位置，或按播放键控制走带
5. 四位一起开演，听完整编曲

乐手上下场都有 0.3~0.5 秒的音量淡入淡出，不会硬切。退场只是停下来，**演奏位置不会清零**：再点他/她上场，或者按播放键，都从刚才停下的地方接着演。退场的乐手是完全静止的，不会跟着别人的音轨做动作。

## 目录

```
index.html          主页面：西部舞台 + 乐手 + 播放条
spine-preview.html  角色调试页：单独看吉他手，切换全部 7 个动画
art/backdrop.png    背景幕布（AI 生成的绘画，压暗虚焦后垫在最底层）
tools/build_single.py  打包脚本：产出一个可单发的单文件 HTML
spine/              角色资源
  angel.*           吉他手（.skel / .atlas / .png）
  phonor.*          主唱唱片小车
  mostma.*          贝斯手（萨克斯从她的图集里取）
  girl.*            鼓手（借来的鼓裁成 drum.png）
  lib/              PixiJS、pixi-spine 3.8、四份打包后的资源数据
guitar.mp3          吉他音轨
singer.mp3          主唱音轨
bass.mp3            贝斯音轨
drums.mp3           鼓组音轨
```

角色是 Spine **3.8.99 二进制**格式，用 PixiJS v7 + pixi-spine 3.8 渲染。因为预览服务器不放行 `.skel` / `.atlas` 后缀，资源已打包成 `spine/lib/*-assets.js`（base64 内嵌），这样本地双击打开也不会被 CORS 拦住。

## 单文件发行版

想直接发给别人（而不是让对方 clone 仓库），可以打成**一个 HTML 文件**，双击就能玩、断网也能玩：

```bash
python tools/build_single.py     # 需要 pillow / lameenc / miniaudio
```

它会把四样东西塞进同一个文件：

| 内容 | 处理方式 |
| ---- | -------- |
| PixiJS、pixi-spine、四份骨骼资源 | 原本就是外部 `<script>`，直接内联 |
| 背景幕布 `art/backdrop.png` | 转成 JPEG(q85) 的 data URI，1.9 MB → 176 KB |
| 四条音轨（各 15 MB / 320 kbps） | 重编码成 128 kbps 再 base64，4×6 MB |

成品约 **37 MB**（原始素材 66 MB），输出在 `release/` 下。这个目录不进 Git —— 单文件产物应该作为 GitHub Release 的附件上传，而不是塞进仓库历史里。

代码里对应的小改动：音轨统一走 `loadTrackBlob()`，发现 `window.EMBED_AUDIO` 里对应名字就直接 base64 解成 Blob，否则照旧 `fetch` 同目录的 mp3。所以同一个 `index.html` 既能当普通版跑，也能被脚本打成单文件版。

## 版本日志

| 版本 | 内容 |
| ---- | ---- |
| v1.0.0 | 乐团成立，鼓手怪兽咚咚报到 🥁 |
| v1.1.0 | 低音怪兽嗡嗡加入，节奏有了厚度 🎸 |
| v1.2.0 | 旋律怪兽叮叮加入，三位合奏成型 🎹 |
| v1.3.0 | 音乐升级：Am–F–C–G 四和弦进行 + 全新主旋律 |
| v1.4.0 | 和声怪兽绵绵加入，四重奏交响乐 🎼 |
| v2.0.0 | 场景重做：换成西部黄昏舞台（酒馆、灯柱、落日、风滚草） |
| v2.1.0 | 吉他手换成 Spine 骨骼角色，加入按 147.28 BPM 编排的弹吉他循环 |
| v2.2.0 | 主唱唱片小车登场，双乐手各自独立开关、音轨同步 |
| v2.3.0 | 贝斯手登场，四支号里选了萨克斯，悬在嘴边随拍送气 |
| v2.4.0 | 鼓手登场，鼓从太鼓角色那儿借来，第 3 拍自己飞过来砸她脑袋，每次换一张随机表情 |
| v2.4.1 | 上场/退场/暂停全部加音量缓入缓出，新乐手插进合奏不再突兀 |
| v2.5.0 | 开场加红丝绒帷幕（拖开才开演）、加「全部开演」一键按钮、背景换成 AI 生成的画布幕布 |
| v2.6.0 | 手机适配：横屏铺满、竖屏装箱并给播放条让位，竖屏天空渐隐消掉硬缝，附一句「横屏更好看」的提醒 |

## 版本控制小课堂

这个仓库本身就是教材：每一次 commit 对应游戏的一个版本，每个 tag 都是一个能玩的完整版本。

```bash
git log --oneline          # 回顾乐团的成长历史
git tag                    # 查看所有版本标签
git show v1.0.0            # 看看第一版改了什么
git diff v2.1.0 v2.2.0     # 对比"加入主唱"这一版动了哪些文件
```

试着回答：主唱唱片小车、贝斯手、鼓手分别是在哪一版加入的？各自带了哪几个新文件？用 `git show` 找找看。

动手试试：给鼓手换一张脸、把砸头改成砸手，或者把间隔从四拍改成两拍——每改一次就提交一次，然后 `git log` 看看你的改动是怎么一步步长成现在这样的。
