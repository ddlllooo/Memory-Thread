import type { Post } from '@/types'

export const mockPosts: Post[] = [
  {
    id: '1',
    title: '搭建个人博客的思考',
    content: `
      <p>一直想拥有一个属于自己的博客，不被平台限制，可以自由地表达想法。经过一番调研，最终选择了 Vue 3 + FastAPI 的技术栈。</p>
      <p>选择 Vue 3 是因为 Composition API 让代码组织更加清晰，配合 TypeScript 能获得很好的开发体验。后端用 FastAPI 则是因为它的性能优异，自动生成 API 文档也省了不少事。</p>
      <p>搭建过程中遇到了不少问题，比如前后端跨域、文件上传、用户认证等，但每一个问题的解决都让我对这些技术有了更深的理解。</p>
      <h3>技术选型总结</h3>
      <ul>
        <li>前端：Vue 3 + TypeScript + Tailwind CSS</li>
        <li>后端：FastAPI + SQLAlchemy + MySQL</li>
        <li>部署：Docker + Nginx</li>
      </ul>
      <p>希望这个博客能成为我记录学习和生活的好地方。</p>
    `,
    excerpt: '记录搭建个人博客的全过程，包括技术选型、遇到的问题和解决方案。',
    images: [
      {
        id: 'img1',
        url: 'https://picsum.photos/seed/blog1/800/400',
        thumbnail: 'https://picsum.photos/seed/blog1/400/200',
        title: '搭建个人博客',
        width: 800,
        height: 400,
        aspectRatio: 2,
        createdAt: '2024-03-10',
        updatedAt: '2024-03-10',
      },
    ],
    tags: ['技术', 'Vue', '博客'],
    published: true,
    createdAt: '2024-03-10',
    updatedAt: '2024-03-10',
  },
  {
    id: '2',
    title: '周末的咖啡馆时光',
    content: `
      <p>周末找了一家安静的咖啡馆，点了一杯手冲，翻开一直想读的那本书。阳光从落地窗洒进来，整个空间都暖洋洋的。</p>
      <p>最近在读《百年孤独》，马尔克斯的魔幻现实主义总是让人沉浸其中，忘记了时间的流逝。书中的马孔多小镇仿佛有自己的生命，每一代人的故事都充满了宿命感。</p>
      <p>偶尔从书中抬起头，看看窗外的行人，听听咖啡机的声音，这种慢节奏的时光真的很治愈。</p>
      <p>生活不只有代码和工作，偶尔停下来感受当下的美好，才能更好地出发。</p>
    `,
    excerpt: '一个安静的周末午后，咖啡、书本和阳光，简单却美好的时光。',
    images: [
      {
        id: 'img2',
        url: 'https://picsum.photos/seed/coffee/800/500',
        thumbnail: 'https://picsum.photos/seed/coffee/400/250',
        title: '咖啡馆',
        width: 800,
        height: 500,
        aspectRatio: 1.6,
        createdAt: '2024-03-15',
        updatedAt: '2024-03-15',
      },
    ],
    tags: ['生活', '读书', '咖啡'],
    published: true,
    createdAt: '2024-03-15',
    updatedAt: '2024-03-15',
  },
  {
    id: '3',
    title: '学习 TypeScript 的一些心得',
    content: `
      <p>从 JavaScript 转到 TypeScript 已经有一段时间了，记录一些心得体会。</p>
      <h3>为什么要用 TypeScript？</h3>
      <p>最直接的好处就是类型安全。很多低级错误（拼写错误、类型不匹配）在编译阶段就能发现，不用等到运行时才报错。对于大型项目来说，类型定义也是一种文档，新成员看类型就能理解数据结构。</p>
      <h3>常见的坑</h3>
      <p>刚开始用的时候，经常被类型报错搞得头疼。尤其是处理第三方库的类型、any 的滥用、泛型的理解等。但坚持下来之后，发现写类型其实是在帮未来的自己省时间。</p>
      <h3>建议</h3>
      <ul>
        <li>不要一开始就追求完美类型，先用 any 再逐步替换</li>
        <li>善用 utility types（Partial, Pick, Omit 等）</li>
        <li>多看优秀开源项目的类型定义</li>
      </ul>
    `,
    excerpt: '从 JavaScript 到 TypeScript 的转型之路，分享踩坑经验和实用技巧。',
    images: [],
    tags: ['技术', 'TypeScript', '前端'],
    published: true,
    createdAt: '2024-04-02',
    updatedAt: '2024-04-02',
  },
  {
    id: '4',
    title: '春日徒步记',
    content: `
      <p>趁着春天天气好，约了几个朋友去郊外徒步。路线选了一条难度适中的山间步道，全程大约 15 公里。</p>
      <p>山里的空气特别清新，路两旁开满了不知名的野花。走了大约两个小时到达一个观景台，从山顶望下去，整个山谷尽收眼底，远处的城市在薄雾中若隐若现。</p>
      <p>下山的时候腿已经开始发抖了，但心情特别好。户外运动的魅力就在于，身体很累但精神很放松。</p>
      <p>回来之后整理了一下装备清单，准备下次挑战更长的路线：</p>
      <ul>
        <li>登山鞋（必须的！）</li>
        <li>足够的水和干粮</li>
        <li>防晒霜和帽子</li>
        <li>充电宝和急救包</li>
      </ul>
    `,
    excerpt: '春暖花开的季节，来一次山间徒步，感受大自然的美好。',
    images: [
      {
        id: 'img3',
        url: 'https://picsum.photos/seed/hiking/800/600',
        thumbnail: 'https://picsum.photos/seed/hiking/400/300',
        title: '山间风景',
        width: 800,
        height: 600,
        aspectRatio: 4 / 3,
        createdAt: '2024-04-10',
        updatedAt: '2024-04-10',
      },
    ],
    tags: ['生活', '户外', '徒步'],
    published: true,
    createdAt: '2024-04-10',
    updatedAt: '2024-04-10',
  },
  {
    id: '5',
    title: 'Docker 部署实践笔记',
    content: `
      <p>最近把个人项目的部署全部迁移到了 Docker，记录一下过程和踩过的坑。</p>
      <h3>为什么用 Docker？</h3>
      <p>最直接的原因是环境一致性。"在我电脑上能跑"这种问题再也不会出现了。另外 Docker Compose 让多服务编排变得很简单，一个 yaml 文件就能定义整个应用栈。</p>
      <h3>实际部署架构</h3>
      <p>目前的架构是 Nginx 做反向代理，前端用 Node 容器构建后拷贝到 Nginx 容器，后端用 Python 容器，数据库用 MySQL 官方镜像。</p>
      <h3>踩过的坑</h3>
      <ul>
        <li>容器内文件权限问题（特别是挂载卷的时候）</li>
        <li>多阶段构建减少镜像体积</li>
        <li>.dockerignore 很重要，不然构建上下文会很大</li>
        <li>健康检查要加上，不然 Docker 不知道服务是否真的就绪</li>
      </ul>
      <p>总的来说，Docker 的学习曲线不算陡，但要真正用好还是需要一些实践经验。</p>
    `,
    excerpt: '将个人项目迁移到 Docker 部署的全过程，包括架构设计和常见问题。',
    images: [],
    tags: ['技术', 'Docker', '部署'],
    published: true,
    createdAt: '2024-04-20',
    updatedAt: '2024-04-20',
  },
  {
    id: '6',
    title: '近期电影推荐',
    content: `
      <p>最近看了几部不错的电影，推荐给大家。</p>
      <h3>《奥本海默》</h3>
      <p>诺兰的又一部力作，三条时间线交叉叙事，节奏紧凑。基里安·墨菲的表演非常出色，把奥本海默的矛盾和挣扎演绎得淋漓尽致。</p>
      <h3>《宇宙探索编辑部》</h3>
      <p>国产科幻的一股清流，用伪纪录片的形式讲了一个关于理想主义的故事。笑中带泪，看完之后久久不能平静。</p>
      <h3>《完美的日子》</h3>
      <p>维姆·文德斯拍摄的东京公厕清洁工的日常，节奏缓慢但充满诗意。让人思考什么才是"好的生活"。</p>
      <p>好的电影不只是娱乐，它能让你看到不同的人生，思考不同的问题。</p>
    `,
    excerpt: '近期看过的几部好电影推荐，涵盖科幻、文艺、纪录片等类型。',
    images: [
      {
        id: 'img4',
        url: 'https://picsum.photos/seed/movie/800/450',
        thumbnail: 'https://picsum.photos/seed/movie/400/225',
        title: '电影',
        width: 800,
        height: 450,
        aspectRatio: 16 / 9,
        createdAt: '2024-05-05',
        updatedAt: '2024-05-05',
      },
    ],
    tags: ['生活', '电影', '推荐'],
    published: true,
    createdAt: '2024-05-05',
    updatedAt: '2024-05-05',
  },
]
