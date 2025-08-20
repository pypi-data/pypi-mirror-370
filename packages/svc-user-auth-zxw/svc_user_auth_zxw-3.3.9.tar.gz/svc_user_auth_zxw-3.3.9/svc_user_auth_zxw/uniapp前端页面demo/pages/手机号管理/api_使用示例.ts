// 手机号管理 API 使用示例代码
// 这个文件展示了如何在不同场景下使用手机号管理的 API

import { 
	updateBindingPhone, 
	sendVerificationCodeForUpdate, 
	getCurrentPhone,
	getCurrentUserInfo,
	type UpdatePhoneRequest 
} from './apis'

/**
 * 示例1: 基本的手机号更新流程
 */
export const basicUpdatePhoneExample = async () => {
	try {
		// 1. 获取当前用户信息
		const currentUser = getCurrentUserInfo()
		if (!currentUser) {
			console.log('用户未登录')
			return
		}
		
		// 2. 显示当前手机号
		const currentPhone = getCurrentPhone()
		console.log('当前绑定手机号:', currentPhone)
		
		// 3. 设置新手机号
		const newPhone = '13800138000'
		
		// 4. 发送验证码
		await sendVerificationCodeForUpdate(newPhone)
		console.log('验证码已发送到新手机号')
		
		// 5. 用户输入验证码后更新手机号
		const smsCode = '123456' // 这应该是用户输入的验证码
		const result = await updateBindingPhone({
			new_phone: newPhone,
			sms_code: smsCode
		})
		
		console.log('手机号更新成功:', result)
		
	} catch (error) {
		console.error('手机号更新失败:', error)
	}
}

/**
 * 示例2: 带验证的手机号更新
 */
export const validateAndUpdatePhone = async (newPhone: string, smsCode: string) => {
	// 验证手机号格式
	if (!isValidPhone(newPhone)) {
		throw new Error('请输入有效的手机号')
	}
	
	// 验证验证码格式
	if (!isValidSmsCode(smsCode)) {
		throw new Error('请输入6位数字验证码')
	}
	
	// 检查是否与当前手机号相同
	const currentPhone = getCurrentPhone()
	if (currentPhone === newPhone) {
		throw new Error('新手机号不能与当前手机号相同')
	}
	
	try {
		// 执行更新
		const result = await updateBindingPhone({
			new_phone: newPhone,
			sms_code: smsCode
		})
		
		return result
	} catch (error) {
		throw error
	}
}

/**
 * 示例3: 带重试机制的验证码发送
 */
export const sendCodeWithRetry = async (phone: string, maxRetries: number = 3) => {
	let retries = 0
	
	while (retries < maxRetries) {
		try {
			await sendVerificationCodeForUpdate(phone)
			console.log('验证码发送成功')
			return true
		} catch (error) {
			retries++
			console.log(`验证码发送失败，第${retries}次重试`)
			
			if (retries >= maxRetries) {
				throw new Error('验证码发送失败，请稍后重试')
			}
			
			// 等待2秒后重试
			await new Promise(resolve => setTimeout(resolve, 2000))
		}
	}
	
	return false
}

/**
 * 示例4: 完整的用户交互流程
 */
export const completeUpdatePhoneFlow = async () => {
	return new Promise<void>((resolve, reject) => {
		// 1. 检查登录状态
		const userInfo = getCurrentUserInfo()
		if (!userInfo) {
			uni.showModal({
				title: '提示',
				content: '请先登录',
				showCancel: false,
				success: () => {
					// 跳转到登录页面
					uni.navigateTo({
						url: '/pages/login/login'
					})
				}
			})
			reject(new Error('用户未登录'))
			return
		}
		
		// 2. 显示当前手机号
		const currentPhone = getCurrentPhone()
		uni.showModal({
			title: '当前绑定手机号',
			content: currentPhone || '未绑定',
			confirmText: '修改',
			cancelText: '取消',
			success: (res) => {
				if (res.confirm) {
					// 3. 跳转到更新页面
					uni.navigateTo({
						url: '/pages/手机号管理/update_phone',
						success: () => resolve(),
						fail: (error) => reject(error)
					})
				} else {
					reject(new Error('用户取消操作'))
				}
			}
		})
	})
}

/**
 * 示例5: 在设置页面中集成手机号管理
 */
export const settingsPageIntegration = {
	// 获取手机号信息用于显示
	getPhoneInfo: () => {
		const phone = getCurrentPhone()
		return phone ? phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2') : '未绑定'
	},
	
	// 检查是否可以修改手机号
	canUpdatePhone: () => {
		return getCurrentUserInfo() !== null
	},
	
	// 导航到手机号管理页面
	navigateToPhoneManagement: () => {
		if (!settingsPageIntegration.canUpdatePhone()) {
			uni.showToast({
				title: '请先登录',
				icon: 'none'
			})
			return
		}
		
		uni.navigateTo({
			url: '/pages/手机号管理/update_phone'
		})
	}
}

// 工具函数
function isValidPhone(phone: string): boolean {
	return /^1[3-9]\d{9}$/.test(phone)
}

function isValidSmsCode(code: string): boolean {
	return /^\d{6}$/.test(code)
}

// 导出所有示例
export const phoneManagementExamples = {
	basicUpdatePhoneExample,
	validateAndUpdatePhone,
	sendCodeWithRetry,
	completeUpdatePhoneFlow,
	settingsPageIntegration
}

// 使用示例：
// import { phoneManagementExamples } from './api_使用示例'
// 
// // 基本使用
// phoneManagementExamples.basicUpdatePhoneExample()
// 
// // 在设置页面中使用
// const phoneDisplay = phoneManagementExamples.settingsPageIntegration.getPhoneInfo()
// console.log('显示的手机号:', phoneDisplay)
//
// // 导航到手机号管理页面
// phoneManagementExamples.settingsPageIntegration.navigateToPhoneManagement()