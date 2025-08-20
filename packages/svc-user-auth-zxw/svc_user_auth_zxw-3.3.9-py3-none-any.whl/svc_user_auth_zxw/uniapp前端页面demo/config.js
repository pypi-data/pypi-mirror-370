// 方式1: 手动切换环境
export const env = 'development' // 'development' | 'production' | 'test'
export const mockEnabled = false
export const REQUEST_TIMEOUT = 5000

// API配置文件
const CONFIG = {
	// 开发环境API地址
	development: {
		apiUrl: 'http://localhost:8000',
		timeout: 10000
	},
	// 生产环境API地址
	production: {
		apiUrl: 'https://api.example.com',
		timeout: 10000
	},
	// 测试环境API地址
	test: {
		apiUrl: 'http://localhost:8000',
		timeout: 10000
	}
}

// 导出完整的API URL构建函数
export const buildApiUrl = (path) => {
	// 确保path以/开头
	if (!path.startsWith('/')) {
		path = '/' + path
	}
	return CONFIG[env].apiUrl + path
}