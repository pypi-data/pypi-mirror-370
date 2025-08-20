<template>
	<view class="example-page">
		<!-- 示例1：基础导航栏 -->
		<CustomNavbar 
			v-if="currentExample === 1"
			title="基础导航栏" 
			@back="handleBack"
			@ready="handleNavbarReady"
		/>
		
		<!-- 示例2：带计时器的导航栏 -->
		<CustomNavbar 
			v-if="currentExample === 2"
			title="计时器导航栏"
			:show-timer="true"
			:timer-text="formatTime(elapsedTime)"
			@back="handleBack"
			@ready="handleNavbarReady"
		/>
		
		<!-- 示例3：带进度条的导航栏 -->
		<CustomNavbar 
			v-if="currentExample === 3"
			title="进度条导航栏"
			:show-progress="true"
			:progress-main-text="`第${currentStep}/${totalSteps}步`"
			:progress-sub-text="`完成度${progressPercent.toFixed(1)}%`"
			:progress-percent="progressPercent"
			@back="handleBack"
			@ready="handleNavbarReady"
		/>
		
		<!-- 示例4：自定义右侧内容 -->
		<CustomNavbar 
			v-if="currentExample === 4"
			title="自定义右侧"
			@back="handleBack"
			@ready="handleNavbarReady"
		>
			<template #right>
				<view class="custom-actions">
					<button class="action-btn" @click="showToast('收藏成功')">
						<text class="action-icon">⭐</text>
					</button>
					<button class="action-btn" @click="showToast('分享成功')">
						<text class="action-icon">📤</text>
					</button>
					<button class="action-btn" @click="showToast('分享成功')">
						<text class="action-icon">📤</text>
					</button>
					<button class="action-btn" @click="showToast('分享成功')">
						<text class="action-icon">📤</text>
					</button>
				</view>
			</template>
		</CustomNavbar>
		
		<!-- 示例5：完整功能导航栏 -->
		<CustomNavbar 
			v-if="currentExample === 5"
			ref="navbarRef"
			title="完整功能"
			:show-timer="true"
			:timer-text="formatTime(elapsedTime)"
			:show-progress="true"
			:progress-main-text="`第${currentStep}/${totalSteps}步`"
			:progress-sub-text="`进度${progressPercent.toFixed(1)}%`"
			:progress-percent="progressPercent"
			:background="customBackground"
			@back="handleBack"
			@ready="handleNavbarReady"
		>
			<template #right>
				<view class="timer-controls">
					<button @click="toggleTimer" class="control-btn">
						{{ isPaused ? '▶️' : '⏸️' }}
					</button>
				</view>
			</template>
			
			<template #content>
				<view class="status-bar">
					<text class="status-text">自定义状态栏1</text>
				</view>
				<view class="status-bar">
					<text class="status-text">自定义状态栏2</text>
				</view>
			</template>
		</CustomNavbar>

		<!-- 页面内容 -->
		<view class="content" :style="{ paddingTop: pageTopPadding + 'px' }">
			<view class="example-selector">
				<text class="selector-title">选择示例：</text>
				<view class="selector-buttons">
					<button 
						v-for="(example, index) in examples" 
						:key="index"
						class="selector-btn"
						:class="{ active: currentExample === index + 1 }"
						@click="switchExample(index + 1)"
					>
						{{ example.name }}
					</button>
				</view>
			</view>

			<view class="example-info">
				<view class="info-card">
					<text class="info-title">{{ currentExampleInfo.name }}</text>
					<text class="info-description">{{ currentExampleInfo.description }}</text>
					
					<view class="info-features">
						<text class="features-title">特性：</text>
						<view class="features-list">
							<text 
								v-for="feature in currentExampleInfo.features" 
								:key="feature"
								class="feature-item"
							>
								• {{ feature }}
							</text>
						</view>
					</view>
					
					<view class="info-controls" v-if="currentExample >= 2">
						<button v-if="currentExample === 2" @click="resetTimer" class="control-button">
							重置计时器
						</button>
						<button v-if="currentExample >= 3" @click="nextStep" class="control-button">
							下一步 ({{ currentStep }}/{{ totalSteps }})
						</button>
						<button v-if="currentExample >= 3" @click="resetProgress" class="control-button">
							重置进度
						</button>
					</view>
				</view>
			</view>

			<view class="debug-info">
				<text class="debug-title">调试信息：</text>
				<view class="debug-item">
					<text class="debug-label">导航栏高度：</text>
					<text class="debug-value">{{ pageTopPadding }}px</text>
				</view>
				<view class="debug-item">
					<text class="debug-label">安全区域高度：</text>
					<text class="debug-value">{{ safeAreaTop }}px</text>
				</view>
				<view class="debug-item">
					<text class="debug-label">状态栏高度：</text>
					<text class="debug-value">{{ statusBarHeight }}px</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import CustomNavbar from './CustomNavbar.vue'

// 响应式数据
const navbarRef = ref(null)
const currentExample = ref(1)
const elapsedTime = ref(0)
const timer = ref(null)
const isPaused = ref(false)
const currentStep = ref(1)
const totalSteps = ref(5)

// 系统信息
const safeAreaTop = ref(0)
const statusBarHeight = ref(0)

// 示例配置
const examples = ref([
	{
		name: '基础',
		description: '最简单的导航栏，只包含标题和返回按钮',
		features: ['标题显示', '返回按钮', '自适应安全区']
	},
	{
		name: '计时器',
		description: '带计时器功能的导航栏，适用于考试或练习场景',
		features: ['计时器显示', '实时更新', '时间格式化']
	},
	{
		name: '进度条',
		description: '带进度条的导航栏，显示当前完成情况',
		features: ['进度条动画', '百分比显示', '步骤信息']
	},
	{
		name: '自定义',
		description: '自定义右侧内容，可以添加操作按钮',
		features: ['右侧插槽', '自定义按钮', '交互反馈']
	},
	{
		name: '完整',
		description: '包含所有功能的完整示例',
		features: ['所有功能', '自定义背景', '内容插槽', '完整控制']
	}
])

// 自定义背景颜色
const customBackground = ref('linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 100%)')

// 计算属性
const currentExampleInfo = computed(() => {
	return examples.value[currentExample.value - 1] || examples.value[0]
})

const progressPercent = computed(() => {
	return (currentStep.value / totalSteps.value) * 100
})

const pageTopPadding = computed(() => {
	if (navbarRef.value) {
		return navbarRef.value.getNavbarHeight() + 20
	}
	return 120 // 默认值
})

// 方法
const formatTime = (seconds) => {
	const minutes = Math.floor(seconds / 60)
	const remainingSeconds = seconds % 60
	return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`
}

const startTimer = () => {
	if (!timer.value) {
		timer.value = setInterval(() => {
			if (!isPaused.value) {
				elapsedTime.value++
			}
		}, 1000)
	}
}

const toggleTimer = () => {
	isPaused.value = !isPaused.value
	showToast(isPaused.value ? '计时器已暂停' : '计时器已恢复')
}

const resetTimer = () => {
	elapsedTime.value = 0
	isPaused.value = false
	showToast('计时器已重置')
}

const nextStep = () => {
	if (currentStep.value < totalSteps.value) {
		currentStep.value++
		showToast(`进入第${currentStep.value}步`)
	} else {
		showToast('已完成所有步骤！')
	}
}

const resetProgress = () => {
	currentStep.value = 1
	showToast('进度已重置')
}

const switchExample = (example) => {
	currentExample.value = example
	showToast(`切换到示例${example}`)
}

const handleBack = () => {
	uni.showModal({
		title: '确认返回',
		content: '确定要返回上一页吗？',
		success: (res) => {
			if (res.confirm) {
				uni.navigateBack()
			}
		}
	})
}

const handleNavbarReady = (data) => {
	safeAreaTop.value = data.safeAreaTop
	statusBarHeight.value = data.statusBarHeight
	console.log('导航栏准备就绪:', data)
}

const showToast = (message) => {
	uni.showToast({
		title: message,
		icon: 'none',
		duration: 1500
	})
}

// 生命周期
onMounted(() => {
	startTimer()
})

onUnmounted(() => {
	if (timer.value) {
		clearInterval(timer.value)
		timer.value = null
	}
})
</script>

<style scoped>
.example-page {
	min-height: 100vh;
	background: #f5f5f5;
}

.content {
	padding: 30rpx;
}

/* 示例选择器 */
.example-selector {
	background: white;
	border-radius: 16rpx;
	padding: 30rpx;
	margin-bottom: 30rpx;
	box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.1);
}

.selector-title {
	font-size: 32rpx;
	font-weight: 600;
	color: #333;
	display: block;
	margin-bottom: 20rpx;
}

.selector-buttons {
	display: flex;
	flex-wrap: wrap;
	gap: 15rpx;
}

.selector-btn {
	padding: 15rpx 25rpx;
	border-radius: 25rpx;
	border: 2rpx solid #e0e0e0;
	background: white;
	color: #666;
	font-size: 26rpx;
	transition: all 0.3s ease;
}

.selector-btn.active {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	color: white;
	border-color: transparent;
}

/* 示例信息 */
.example-info {
	margin-bottom: 30rpx;
}

.info-card {
	background: white;
	border-radius: 16rpx;
	padding: 30rpx;
	box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.1);
}

.info-title {
	font-size: 36rpx;
	font-weight: 600;
	color: #333;
	display: block;
	margin-bottom: 15rpx;
}

.info-description {
	font-size: 28rpx;
	color: #666;
	line-height: 1.6;
	display: block;
	margin-bottom: 25rpx;
}

.info-features {
	margin-bottom: 25rpx;
}

.features-title {
	font-size: 30rpx;
	font-weight: 500;
	color: #333;
	display: block;
	margin-bottom: 15rpx;
}

.features-list {
	background: #f8f9ff;
	border-radius: 8rpx;
	padding: 20rpx;
}

.feature-item {
	font-size: 26rpx;
	color: #4facfe;
	display: block;
	margin-bottom: 8rpx;
	line-height: 1.4;
}

.feature-item:last-child {
	margin-bottom: 0;
}

.info-controls {
	display: flex;
	flex-wrap: wrap;
	gap: 15rpx;
}

.control-button {
	padding: 12rpx 20rpx;
	border-radius: 20rpx;
	background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
	color: white;
	border: none;
	font-size: 24rpx;
	transition: all 0.3s ease;
}

.control-button:active {
	transform: scale(0.95);
}

/* 自定义导航栏内容 */
.custom-actions {
	display: flex;
	gap: 15rpx;
}

.action-btn {
	width: 60rpx;
	height: 60rpx;
	border-radius: 30rpx;
	background: rgba(255, 255, 255, 0.2);
	border: none;
	display: flex;
	align-items: center;
	justify-content: center;
	transition: all 0.3s ease;
}

.action-btn:active {
	background: rgba(255, 255, 255, 0.4);
	transform: scale(0.9);
}

.action-icon {
	font-size: 28rpx;
}

.timer-controls {
	display: flex;
	align-items: center;
}

.control-btn {
	width: 60rpx;
	height: 60rpx;
	border-radius: 30rpx;
	background: rgba(255, 255, 255, 0.3);
	border: none;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 24rpx;
	transition: all 0.3s ease;
}

.control-btn:active {
	background: rgba(255, 255, 255, 0.5);
	transform: scale(0.9);
}

.status-bar {
	text-align: center;
	padding: 10rpx 0;
	background: rgba(255, 255, 255, 0.1);
	border-radius: 8rpx;
	margin-top: 10rpx;
}

.status-text {
	color: rgba(255, 255, 255, 0.8);
	font-size: 24rpx;
}

/* 调试信息 */
.debug-info {
	background: white;
	border-radius: 16rpx;
	padding: 30rpx;
	box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.1);
}

.debug-title {
	font-size: 32rpx;
	font-weight: 600;
	color: #333;
	display: block;
	margin-bottom: 20rpx;
}

.debug-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 15rpx 0;
	border-bottom: 1rpx solid #f0f0f0;
}

.debug-item:last-child {
	border-bottom: none;
}

.debug-label {
	font-size: 28rpx;
	color: #666;
}

.debug-value {
	font-size: 28rpx;
	color: #4facfe;
	font-weight: 500;
}
</style> 