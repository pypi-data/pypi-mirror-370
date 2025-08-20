<template>
	<view class="custom-navbar" :style="{ paddingTop: safeAreaTop + 'px' }">
		<!-- 导航栏顶部 -->
		<view class="navbar-top">
			<view class="navbar-left">
				<view v-if="showBackBtn" class="back-btn" @click="handleBack">
					<text class="back-icon">{{ backIcon }}</text>
				</view>
				<text class="navbar-title">{{ title }}</text>
			</view>
			<view class="navbar-right">
				<!-- 计时器显示 -->
				<view v-if="showTimer" class="timer-display">
					<text class="timer-text">{{ timerText }}</text>
				</view>
				<!-- 自定义右侧插槽 -->
				<slot name="right"></slot>
			</view>
		</view>

		<!-- 进度信息栏 -->
		<view v-if="showProgress" class="progress-info-bar">
			<!-- 进度文字信息 -->
			<view class="progress-text-row">
				<text class="progress-main">{{ progressMainText }}</text>
				<text class="progress-sub">{{ progressSubText }}</text>
			</view>
			<!-- 进度条 -->
			<view class="progress-container">
				<view class="progress-bar">
					<view class="progress-fill" :style="{ width: progressPercent + '%' }"></view>
				</view>
			</view>
		</view>

		<!-- 自定义内容插槽 -->
		<slot name="content"></slot>

		<!-- 开发调试信息（可选显示） -->
		<view v-if="showDebug" class="debug-info">
			<text class="debug-text">状态栏: {{ statusBarHeight }}px | 安全区: {{ safeAreaTop }}px</text>
		</view>
	</view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getSystemInfo } from '@/src/utils/systemInfo'

// 定义组件属性
const props = defineProps({
	// 基础属性
	title: {
		type: String,
		default: '标题'
	},
	// 返回按钮
	showBackBtn: {
		type: Boolean,
		default: true
	},
	backIcon: {
		type: String,
		default: '←'
	},
	// 计时器
	showTimer: {
		type: Boolean,
		default: false
	},
	timerText: {
		type: String,
		default: '00:00'
	},
	// 进度条
	showProgress: {
		type: Boolean,
		default: false
	},
	progressMainText: {
		type: String,
		default: ''
	},
	progressSubText: {
		type: String,
		default: ''
	},
	progressPercent: {
		type: Number,
		default: 0
	},
	// 调试信息
	showDebug: {
		type: Boolean,
		default: false
	},
	// 自定义样式
	background: {
		type: String,
		default: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
	}
})

// 定义事件
const emit = defineEmits(['back', 'ready'])

// 响应式数据
const systemInfo = ref({})
const statusBarHeight = ref(0)
const safeAreaTop = ref(0)

// 初始化系统信息
const initSystemInfo = () => {
	const { systemInfo: info, statusBarHeight: barHeight, safeAreaTop: safeTop } = getSystemInfo()
	systemInfo.value = info
	statusBarHeight.value = barHeight
	safeAreaTop.value = safeTop
	
	// 通知父组件系统信息已准备好
	emit('ready', {
		systemInfo: info,
		statusBarHeight: barHeight,
		safeAreaTop: safeTop
	})
}

// 返回按钮点击处理
const handleBack = () => {
	emit('back')
}

// 计算导航栏高度供父组件使用
const getNavbarHeight = () => {
	let height = safeAreaTop.value + 40 // 基础导航栏高度
	if (props.showProgress) {
		height += 60 // 进度栏高度
	}
	return height
}

// 生命周期
onMounted(() => {
	initSystemInfo()
})

// 暴露方法给父组件
defineExpose({
	getNavbarHeight,
	systemInfo: computed(() => systemInfo.value),
	statusBarHeight: computed(() => statusBarHeight.value),
	safeAreaTop: computed(() => safeAreaTop.value)
})
</script>

<style scoped>
.custom-navbar {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	background: v-bind(background);
	padding-left: 30rpx;
	padding-right: 30rpx;
	padding-bottom: 15rpx;
	box-shadow: 0 2rpx 20rpx rgba(0, 0, 0, 0.1);
	z-index: 1000;
}

/* 导航栏顶部 */
.navbar-top {
	display: flex;
	justify-content: space-between;
	align-items: center;
	height: 40px;
}

.navbar-left {
	display: flex;
	align-items: center;
}

.back-btn {
	width: 40rpx;
	height: 40rpx;
	border-radius: 50%;
	display: flex;
	justify-content: center;
	align-items: center;
	margin-right: 20rpx;
	transition: all 0.3s ease;
}

.back-btn:active {
	background: rgba(255, 255, 255, 0.2);
	transform: scale(0.9);
}

.back-icon {
	font-size: 28rpx;
	font-weight: bold;
	color: #ffffff;
}

.navbar-title {
	font-size: 32rpx;
	font-weight: 600;
	color: #ffffff;
}

.navbar-right {
	display: flex;
	align-items: center;
}

.timer-display {
	padding: 8rpx 20rpx;
	border-radius: 20rpx;
	background: rgba(255, 255, 255, 0.2);
	margin-right: 20rpx;
}

.timer-text {
	font-size: 28rpx;
	font-weight: 500;
	color: #ffffff;
}

/* 进度信息栏 */
.progress-info-bar {
	margin-top: 15rpx;
	margin-bottom: 15rpx;
}

.progress-text-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 15rpx;
}

.progress-main {
	font-size: 30rpx;
	font-weight: 600;
	color: #ffffff;
}

.progress-sub {
	font-size: 26rpx;
	font-weight: 500;
	color: rgba(255, 255, 255, 0.8);
}

.progress-container {
	width: 100%;
}

.progress-bar {
	height: 8rpx;
	background: rgba(255, 255, 255, 0.3);
	border-radius: 4rpx;
	overflow: hidden;
}

.progress-fill {
	height: 100%;
	background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
	border-radius: 4rpx;
	transition: width 0.3s ease;
	box-shadow: 0 0 10rpx rgba(102, 126, 234, 0.3);
}

/* 开发调试信息样式 */
.debug-info {
	text-align: center;
	padding: 5rpx 0;
	background: rgba(255, 255, 255, 0.1);
	margin-top: 10rpx;
	border-radius: 10rpx;
}

.debug-text {
	font-size: 20rpx;
	color: rgba(255, 255, 255, 0.7);
}
</style> 