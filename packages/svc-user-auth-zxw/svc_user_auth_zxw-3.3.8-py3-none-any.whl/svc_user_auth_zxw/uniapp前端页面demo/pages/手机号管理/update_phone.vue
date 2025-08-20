<template>
	<view class="container">
		<view class="header">
			<text class="title">更新绑定手机号</text>
		</view>
		
		<view class="form-container">
			<!-- 当前手机号显示 -->
			<view class="current-phone-section">
				<text class="label">当前绑定手机号：</text>
				<text class="current-phone">{{ currentPhone || '未绑定' }}</text>
			</view>
			
			<!-- 新手机号输入 -->
			<view class="input-group">
				<text class="label">新手机号：</text>
				<input 
					class="input" 
					type="number" 
					placeholder="请输入新手机号"
					v-model="newPhone"
					maxlength="11"
				/>
			</view>
			
			<!-- 验证码输入 -->
			<view class="input-group">
				<text class="label">验证码：</text>
				<view class="code-input-container">
					<input 
						class="input code-input" 
						type="number" 
						placeholder="请输入验证码"
						v-model="smsCode"
						maxlength="6"
					/>
					<button 
						class="send-code-btn"
						:disabled="!canSendCode || sendCodeCountdown > 0"
						@click="sendCode"
					>
						{{ sendCodeText }}
					</button>
				</view>
			</view>
			
			<!-- 更新按钮 -->
			<button 
				class="update-btn"
				:disabled="!canUpdate || isUpdating"
				@click="updatePhone"
			>
				{{ isUpdating ? '更新中...' : '更新手机号' }}
			</button>
		</view>
	</view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { 
	updateBindingPhone, 
	sendVerificationCodeForUpdate, 
	getCurrentPhone 
} from './apis'

// 响应式数据
const currentPhone = ref<string>('')
const newPhone = ref<string>('')
const smsCode = ref<string>('')
const isUpdating = ref<boolean>(false)
const sendCodeCountdown = ref<number>(0)

// 计算属性
const canSendCode = computed(() => {
	return newPhone.value.length === 11 && /^1[3-9]\d{9}$/.test(newPhone.value)
})

const canUpdate = computed(() => {
	return canSendCode.value && smsCode.value.length === 6
})

const sendCodeText = computed(() => {
	if (sendCodeCountdown.value > 0) {
		return `${sendCodeCountdown.value}s后重发`
	}
	return '发送验证码'
})

// 发送验证码倒计时
let countdownTimer: number | null = null

const startCountdown = () => {
	sendCodeCountdown.value = 60
	countdownTimer = setInterval(() => {
		sendCodeCountdown.value--
		if (sendCodeCountdown.value <= 0) {
			clearInterval(countdownTimer!)
			countdownTimer = null
		}
	}, 1000)
}

// 发送验证码
const sendCode = async () => {
	if (!canSendCode.value || sendCodeCountdown.value > 0) return
	
	try {
		uni.showLoading({ title: '发送中...' })
		
		await sendVerificationCodeForUpdate(newPhone.value)
		
		uni.hideLoading()
		uni.showToast({
			title: '验证码已发送',
			icon: 'success'
		})
		
		startCountdown()
	} catch (error) {
		uni.hideLoading()
		console.error('发送验证码失败:', error)
		// 错误提示已在 request 函数中处理
	}
}

// 更新手机号
const updatePhone = async () => {
	if (!canUpdate.value || isUpdating.value) return
	
	try {
		isUpdating.value = true
		uni.showLoading({ title: '更新中...' })
		
		await updateBindingPhone({
			new_phone: newPhone.value,
			sms_code: smsCode.value
		})
		
		uni.hideLoading()
		uni.showToast({
			title: '手机号更新成功',
			icon: 'success'
		})
		
		// 更新当前手机号显示
		currentPhone.value = newPhone.value
		
		// 清空输入框
		newPhone.value = ''
		smsCode.value = ''
		
		// 可以选择跳转到其他页面或执行其他操作
		setTimeout(() => {
			uni.navigateBack()
		}, 1500)
		
	} catch (error) {
		uni.hideLoading()
		console.error('更新手机号失败:', error)
		// 错误提示已在 request 函数中处理
	} finally {
		isUpdating.value = false
	}
}

// 页面加载时获取当前手机号
onMounted(() => {
	const phone = getCurrentPhone()
	if (phone) {
		currentPhone.value = phone
	}
})

// 页面卸载时清理定时器
onUnmounted(() => {
	if (countdownTimer) {
		clearInterval(countdownTimer)
	}
})
</script>

<style scoped>
.container {
	padding: 40rpx;
	background-color: #f8f9fa;
	min-height: 100vh;
}

.header {
	text-align: center;
	margin-bottom: 60rpx;
}

.title {
	font-size: 48rpx;
	font-weight: bold;
	color: #333;
}

.form-container {
	background-color: #fff;
	border-radius: 20rpx;
	padding: 40rpx;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.1);
}

.current-phone-section {
	margin-bottom: 40rpx;
	padding: 30rpx;
	background-color: #f1f3f4;
	border-radius: 12rpx;
}

.current-phone {
	color: #1976d2;
	font-weight: bold;
	font-size: 32rpx;
}

.input-group {
	margin-bottom: 40rpx;
}

.label {
	display: block;
	font-size: 28rpx;
	color: #666;
	margin-bottom: 12rpx;
}

.input {
	width: 100%;
	height: 88rpx;
	border: 2rpx solid #e0e0e0;
	border-radius: 12rpx;
	padding: 0 20rpx;
	font-size: 32rpx;
	background-color: #fff;
	box-sizing: border-box;
}

.input:focus {
	border-color: #1976d2;
	outline: none;
}

.code-input-container {
	display: flex;
	gap: 20rpx;
}

.code-input {
	flex: 1;
}

.send-code-btn {
	width: 200rpx;
	height: 88rpx;
	background-color: #1976d2;
	color: #fff;
	border: none;
	border-radius: 12rpx;
	font-size: 24rpx;
	display: flex;
	align-items: center;
	justify-content: center;
}

.send-code-btn:disabled {
	background-color: #ccc;
	color: #999;
}

.update-btn {
	width: 100%;
	height: 88rpx;
	background-color: #1976d2;
	color: #fff;
	border: none;
	border-radius: 12rpx;
	font-size: 32rpx;
	margin-top: 40rpx;
}

.update-btn:disabled {
	background-color: #ccc;
	color: #999;
}

.update-btn:not(:disabled):active {
	background-color: #1565c0;
}
</style>