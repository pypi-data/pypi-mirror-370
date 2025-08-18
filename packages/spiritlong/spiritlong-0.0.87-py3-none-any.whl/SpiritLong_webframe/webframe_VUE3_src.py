

def write_VUE3_src_files
	# ----------------------------------- src -----------------------------------
	with open(f'{path}/src/App.vue', 'w') as f:
		f.write(webframe_VUE3_App_vue.content)
	
	with open(f'{path}/src/main.js', 'w') as f:
		f.write(webframe_VUE3_src.content_main_js)

	with open(f'{path}/src/webframe.js', 'w') as f:
		f.write(webframe_VUE3_src.content_webframe_js)






# =================================== main.js ===================================
content_main_js	= '''/******************************************************************
 *             ____     _     _ __  __                 
 *            / __/__  (_)___(_) /_/ /  ___  ___  ___ _
 *           _\\ \\/ _ \\/ / __/ / __/ /__/ _ \\/ _ \\/ _ `/
 *          /___/ .__/_/_/ /_/\\__/____/\\___/_//_/\\_, / 
 *             /_/                              /___/  
 *
 *Copyright (c) 2025 Chongqing Spiritlong Technology Co., Ltd.
 *All rights reserved.
 *@author	arthuryang
 *@brief	主javascript，从index.html开始运行
 ******************************************************************/

// Vconsole供调试	  
import	Vconsole	from 'vconsole';
new Vconsole();

// 仓库，作为全局变量使用
import { createPinia, defineStore }		from 'pinia'
const pinia = createPinia()
export const main_store = defineStore('main', {
	// 变量及其初值
	state: () => {
		return {
			login_enabled		: false,	// 是否显示login layout
			viewport_message_show	: false,	// 是否显示全屏消息
			websocket_connected	: false,	// 是否连接成功
			loading			: false,	// 是否显示loading
		}
	},
})

// 创建路由实例，只包含基本路由
const base_URL = import.meta.env.BASE_URL
import { createRouter, createWebHistory }	from 'vue-router'
export const router = createRouter({
	history: createWebHistory(base_URL),
	routes: [
		{	path : '/',			name : 'root',	redirect	: '/'					},
		{	path : '/:pathMatch(.*)',	name : '404',	component	: () => import('./views/404.vue')	}
	]
})

// =========================== APP ============
// 创建App对象app
import { createApp }	from 'vue'
import App		from './App.vue'
const app = createApp(App)

// 安装路由
app.use(router)
	  
// 安装仓库
app.use(pinia)

// 初始化webframe
import {webframe_initialize} from './library/webframe.js'

// 注册components下的所有组件
import register_components from './components/index.vue'
register_components(app)

// 建立websocket连接
import { API, wait, window_websocket }	from './webframe'
import application_config	from './application_config'
window.websocket = new window_websocket(application_config.websocket_URL)

wait(()=>main_store().websocket_connected).then(() => {
	const	parameters	= new URLSearchParams(location.search);
	const	code		= parameters.get('code');
	const	token		= localStorage.getItem('token');
	if (code && !token) {
		// 第二次进入有code，调用API进行认证返回token
		API('/login_wechat', {wechat_code: code});
	}else{
		// 首次加载app没有微信code时，直接mount后会调用接口返回401
		// 然后调用webframe中的wechat_code_redirect函数获取到code
		app.mount('#app');
	}
})
'''
# =================================== webframe.js ===================================
content_webframe_js	= '''/******************************************************************
 *             ____     _     _ __  __                 
 *            / __/__  (_)___(_) /_/ /  ___  ___  ___ _
 *           _\\ \\/ _ \\/ / __/ / __/ /__/ _ \\/ _ \\/ _ `/
 *          /___/ .__/_/_/ /_/\\__/____/\\___/_//_/\\_, / 
 *             /_/                              /___/  
 *
 *Copyright (c) 2025 Chongqing Spiritlong Technology Co., Ltd.
 *All rights reserved.
 *@author	arthuryang
 *@brief	
 ******************************************************************/

import { reactive }		from 'vue'
import axios			from 'axios'
import { nanoid }		from 'nanoid'
import application_config	from './application_config'
import { main_store, router }		from './main'

// -----------------------------axios 请求封装-----------------------------
// axios实例
const API_axios_POST = axios.create({
	baseURL	: '/API',
	timeout	: 10000,
	headers	: {
		'Content-Type'	: 'application/json',
	}
})

/**
 * 全局请求函数：封装成更加简洁的形式
 * 必定是POST
 * 注意：使用此函数的方法为：
 * 	API(URL, data).then(response=>{
 * 		// 此处为API返回处理代码
 * 	}).catch(error=>{
 * 		// 这是错误处理的代码
 * 	})
 * 此函数的执行仍然是异步的
 * @param {String}	URL	路径
 * @param {Object}	data	请求时附带的数据，默认为{}
 * @returns 
 */
export function API(URL, data = {}, callback = null) {
	// 使用
	return new Promise((resolve, reject) => {
		if (!URL) {
			console.error('URL is required');
			return;
		}
		// 发送请求
		API_axios_POST.post(URL, data)
			.then((response) => {
				resolve(response);
			})
			.catch((error) => {
				// 错误处理：简单打印错误消息
				console.log('响应错误', error)
				reject(error);
			});
	});
}

/** 
 * 获取微信code，执行此函数后将访问open.weixin.qq.com，然后重定向到给定的URL
 * @param {String}	redirect_URL	要跳转的路径
 * @param {String}	app_ID		微信appID
 * @param {String}	state		自定义字符串，a-zA-Z0-9的参数值，最多128字节，用于区分跳转前后
 * @returns
 */
export function wechat_code_redirect(redirect_URL, app_ID, state = nanoid()) {
	// 只有微信客户端才能使用此功能
	let is_wechat = /MicroMessenger/i.test(window.navigator.userAgent)
	if (!is_wechat) {
		// 不是微信浏览器才展示登录界面
		main_store().login_enabled = true;
		return ''
	}
	// 只要求获得openid，无需弹出授权页面
	let scope = 'snsapi_base';
	let wechat_URL = 'https://open.weixin.qq.com/connect/oauth2/authorize?' +
		`appid=${app_ID}` +
		`&redirect_uri=${encodeURIComponent(redirect_URL)}` +
		`&response_type=code` +
		`&scope=${scope}` +
		`&state=${state}` +
		'#wechat_redirect'
	// 跳转
	window.location.href = wechat_URL;
}

// 请求拦截器
API_axios_POST.interceptors.request.use(
	config => {
		// 添加请求头
		// if (localStorage.getItem('token')) {
		// 	config.headers['Authorization']	= `Bearer ${localStorage.getItem('token')}`;
		// }
		config.headers['Authorization']		= `Bearer ${localStorage.getItem('token')}`;

		// 总是添加websocket_code
		config.headers['Websocket-Code']	= localStorage.getItem('websocket_code');

		// 仅访问login_wechat时，添加wechat_code


		return config;
	},
	error => {
		return Promise.reject(error)
	}
)

// 响应拦截器
API_axios_POST.interceptors.response.use(
	response => {
		if (response.status==200) {
			return response.data.data;
		}
		return response.data;
	},
	error => {
		main_store().loading = false;
		switch (error.response.status) {
			case 400:	// 请求中包含错误
				console.log("请求中包含错误：错误/缺失的参数/路由")
				break;
			case 401:	// 需要登录才可访问
				localStorage.removeItem('token');
				wechat_code_redirect(window.location.href, application_config.wechat_app_ID);
				break;
			case 403:	// 权限不足
				console.log(router)
				router.push('/403');
				break;
			default:
				console.log("返回其他代码：" + error.response.status);
		}
	}
)

/**
 * 同步等待函数
 * @param {Function}	check	检查函数
 * @param {Number}	ms	检查间隔时间
 */
export async function wait(check, ms=100) {
	try {
		await (() => {
			return new Promise((resolve, reject) => {
				// 每隔ms检查一次
				const check_interval = setInterval(() => {
					if (check()) {
						clearInterval(check_interval);
						clearTimeout(timeout);
						resolve();
					}
				}, ms);
				// 10秒等待超时
				const timeout = setTimeout(() => {
					if (!check()) {
						clearInterval(check_interval);
						clearTimeout(timeout);
						reject();
					}
				}, 1000);
			});
		})();
	} catch (error) {
		console.log('等待超时', error);
	}
}

// ----------------------------- websocket客户端 -----------------------------
// 消息类型枚举
const MESSAGE_TYPE = {
	CONNECTED	: 'C',	// 连接成功
	TOKEN		: 'T',	// 返回TOKEN
	PUBLISH		: 'P',	// 推送数据
	USER		: 'U',	// 推送用户信息
}

// 使用类来实现
export class window_websocket {
	// 连接对象 
	websocket			= null;
	// 重连超时时间
	reconnect_timeout		= 1000;
	// 最大重连次数
	max_reconnect_times		= 10;
	// 当前重连次数
	current_reconnect_times		= 0;
	// 重连计时器
	reconnect_timer			= null;
	// 处理推送数据的回调函数
	static publish_callback		= null;
	// 消息队列，根据table_ID分组存储消息
	static message_queues		= {};
	// 处理队列的定时器
	static process_timer		= null;
	// 批处理延迟时间（毫秒）
	static BATCH_PROCESS_DELAY	= 100;

	// 构造函数
	//	URL	websocket地址字符串
	constructor(URL) {
		// 开始连接
		this.websocket = new WebSocket(URL);

		// 设置事件监听/回调函数
		this.websocket.onopen		= this.websocket_onopen;
		this.websocket.onmessage	= this.websocket_onmessage;
		this.websocket.onclose		= this.websocket_onclose;
		this.websocket.onerror		= this.websocket_onerror;
	}

	/// websocket的回调函数：连接成功
	websocket_onopen(event) {
		console.log('websocket连接成功', event.target.url)
	}

	/// websocket的回调函数：
	websocket_onmessage(event) {
		const event_data	= event.data;

		// 消息类型
		const message_type	= event_data[0];
		const message_data	= event_data.slice(1);
		// console.log('接收到后端发送的websocket消息，消息类型：', message_type, '，消息数据：', message_data)
		// 每个消息的第一个字节表示消息类型
		// C	CONNECTED：已经连接，后继是websocket_code
		// T	TOKEN：更新TOKEN，后继是token
		// P	PUBLISH：订阅发布，后继是JSON字符串，UTF-8解码，每个key是channel名称。一条消息中可以包含多个channel以提升效率
		switch (message_type) {
			case MESSAGE_TYPE.CONNECTED:
				// 连接成功，存储websocket_code
				localStorage.setItem('websocket_code', message_data);
				main_store().websocket_connected = true;
				break;
			case MESSAGE_TYPE.TOKEN:
				localStorage.setItem('token', message_data);
				location.reload();
				break;
			case MESSAGE_TYPE.USER:
				localStorage.setItem('user_information', message_data);
				break;
			case MESSAGE_TYPE.PUBLISH:
				// 内容解析为字典 utf-8解码
				let data	= {};
				try {
					data	= JSON.parse(message_data);
				} catch (error) {
					console.log('解析data失败：', error)
					return;
				}
				console.log('发布数据', data)
				// 处理收到的发布数据，data格式为[`VD ${table_ID} ${ID}`, {record_key, record_value}]
				const channel		= data[0];
				const channel_data	= data[1];
				const table_ID		= channel.split(' ')[1];
				const record_ID		= channel.split(' ')[2];
				// 初始化该table_ID的队列
				if (!window_websocket.message_queues[table_ID]) {
					window_websocket.message_queues[table_ID]	= [];
				}
				// 添加记录，添加记录ID
				window_websocket.message_queues[table_ID].push({
					ID	: record_ID,
					...channel_data
				});
				// 处理每次订阅的所有记录
				if (!window_websocket.process_timer) {
					window_websocket.process_timer = setTimeout(
						window_websocket.process_message_queues, 
						window_websocket.BATCH_PROCESS_DELAY
					);
				}
				break;
			default:
				;
		}
	}

	// 合并同一table_ID的消息后调用回调函数
	static process_message_queues() {
		if (!window_websocket.publish_callback||Object.keys(window_websocket.message_queues).length===0) {
			return;
		}
		// 合并所有视图表的记录
		const merged_data	= {};
		// 处理每个table_ID的队列
		for (const table_ID in window_websocket.message_queues) {
			if (window_websocket.message_queues[table_ID].length===0) {
				continue;
			}
			// 将同一table_ID的所有消息按ID分组并合并字段, 保留最新的记录
			const record_map	= new Map();
			window_websocket.message_queues[table_ID].forEach(record => {
				record_map.set(record.ID, record);
			});
			const table_records = Array.from(record_map.values());
			merged_data[table_ID]				= table_records;
			// 清空该table_ID的队列
			window_websocket.message_queues[table_ID]	= [];
		}
		
		// 调用回调函数处理合并后的数据
		if (Object.keys(merged_data).length > 0) {
			window_websocket.publish_callback(merged_data);
		}
		
		// 重置处理定时器
		clearTimeout(window_websocket.process_timer);
		window_websocket.process_timer		= null;
	}

	// 设置处理推送数据的回调函数
	static set_publish_callback(callback) {
		window_websocket.publish_callback	= callback;
	}
}

// ----------------------------- ID列表压缩/解压工具 -----------------------------
/**
 * 解析ID字符串为数组（对应webframe.py的id_string_encode）
 * @param {String} id_string 格式如: "1,2,3-5"
 * @returns {Array} 排序后的数字数组
 */
export function ID_string_encode(id_string) {
	if (!id_string||typeof id_string!=='string') {
		return [];
	}
	const parts		= id_string.split(',');
	const trimmed_parts	= parts.map(part => part.trim());
	const filtered_parts	= trimmed_parts.filter(part => part.length > 0);
	const flat_mapped_parts	= filtered_parts.flatMap(part => {
		if (part.includes('-')) {
			const [start_str, end_str]	= part.split('-');
			const start			= parseInt(start_str, 10);
			const end			= parseInt(end_str, 10);

			if (isNaN(start)||isNaN(end)||start>end) {
				return [];
			}

			return Array.from({ length: end-start+1 }, (_, i)=>start+i);
		}

		const num	= parseInt(part, 10);
		return isNaN(num)?[]:[num];
	});
	const unique_parts	= flat_mapped_parts.filter((n, index, arr) => arr.indexOf(n) === index); // 去重
	const sorted_parts	= unique_parts.sort((a, b) => a - b);
	return sorted_parts;
}

/**
 * 压缩ID数组为字符串（对应webframe.py的id_string_decode）
 * @param	{Array}		id_list	数字数组
 * @returns	{String}		压缩后的字符串
 */
export function ID_string_decode(id_list) {
	if (!Array.isArray(id_list)||id_list.length===0) {
		return "";
	}
	// 去重并排序
	const unique_sorted	= [...new Set(id_list)].map(Number).filter(n=>!isNaN(n));
	if (unique_sorted.length===0) {
		return "";
	}
	let result	= [];
	let start	= unique_sorted[0];
	let current	= start;
	for (let i=1; i<unique_sorted.length; i++) {
		if (unique_sorted[i]===current+1) {
			current	= unique_sorted[i];
		} else {
			result.push(start===current?start:`${start}-${current}`);
			start	= current=unique_sorted[i];
		}
	}

	result.push(start===current?start:`${start}-${current}`);
	return result.join(',');
}

// ----------------------------- 日期时间工具函数 -----------------------------

// 格式化日期
// date:	日期对象
// format:	格式字符串
export function _format_date(date, format='YYYY-MM-DD') {
	const year	= date.getFullYear();
	const month	= String(date.getMonth()+1).padStart(2, '0');
	const day	= String(date.getDate()).padStart(2, '0');
	const hour	= String(date.getHours()).padStart(2, '0');
	const minute	= String(date.getMinutes()).padStart(2, '0');
	const second	= String(date.getSeconds()).padStart(2, '0');
	let formatted_date = format.replace('YYYY', year).replace('MM', month).replace('DD', day);
	if (format.includes('HH:mm:ss')) {
		formatted_date	+= ` ${hour}:${minute}:${second}`;
	}
	return formatted_date;
}

// 格式化日期
// date:	日期对象或日期字符串
// separator:	日期分隔符
export function format_date(date, separator='-') {
	if (typeof date==='string') {
		date	= new Date(date);
	}
	return _format_date(date, `YYYY${separator}MM${separator}DD`);
}

// 格式化日期时间
// date:	日期对象或日期字符串
// separator:	日期分隔符
export function format_datetime(date, separator='-') {
	if (typeof date==='string') {
		date	= new Date(date);
	}
	return _format_date(date, `YYYY${separator}MM${separator}DD HH:mm:ss`);
}

// 根据日期字符串获取当天截止时间
// date_str:	日期字符串
export function get_today_end_time(date_str) {
	const date = new Date(date_str);
	date.setHours(23, 59, 59, 999);
	return date;
}

// 获取指定天数后的日期
// days:	天数
export function get_date_by_days(days) {
	return new Date(Date.now() + days * 24 * 60 * 60 * 1000);
}

//=================================视图数据管理===================================

export class VIEW_DATA {
	constructor(view_name) {
		// 视图名称
		this.view_name			= view_name||'default'
		// 视图表ID列表
		this.view_table_IDs		= reactive({})
		// 视图表ID列表的初始订阅index
		this.view_table_initial_index	= reactive({})
		// 视图更新loading
		this.loading			= reactive({})
	}

	/**
	 * 更新数据
	 * @param {Array}	table_IDs	表ID列表
	 * @param {Object}	condition	条件参数
	 */
	async update_data(table_IDs=[], condition={}) {
		try {
			this.loading	= true
			const tables	= {}

			// 获取ID列表
			const data = await API('/view_table_query', {
				view		: this.view_name,
				condition	: condition,
			})

			// 处理返回的数据
			for (const view_table_ID in data) {
				const all_ID_string				= data[view_table_ID].split(';')[0]
				const initial_index_string			= data[view_table_ID].split(';')[1]
				this.view_table_IDs[view_table_ID]		= ID_string_encode(all_ID_string)
				this.view_table_initial_index[view_table_ID]	= ID_string_encode(initial_index_string)
			}

			// 初始订阅
			for (const view_table_ID in this.view_table_IDs) {
				if (table_IDs.length>0&&!table_IDs.includes(view_table_ID)) {
					continue;
				}
				// ;之前是订阅，;之后是退订
				const initial_subscribe_length	= this.view_table_initial_index[view_table_ID].length
				tables[view_table_ID]	= ID_string_decode(this.view_table_IDs[view_table_ID].slice(0, initial_subscribe_length)) + ';'
			}

			// 订阅ID列表
			await API('/view_subscribe', {
				view	: this.view_name,
				tables	: tables,
			})
		} catch (error) {
			console.error('更新数据失败', error)
		} finally {
			this.loading	= false
			main_store().loading = false
		}
	}
}
'''

# =================================== component/webframe_login.vue ===================================

# =================================== component/webframe_header.vue ===================================

# =================================== component/webframe_sider.vue ===================================

