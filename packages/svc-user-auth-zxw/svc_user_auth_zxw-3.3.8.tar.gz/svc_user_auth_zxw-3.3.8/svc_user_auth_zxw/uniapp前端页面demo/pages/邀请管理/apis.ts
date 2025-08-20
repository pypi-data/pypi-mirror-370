import { buildApiUrl } from '@/config.js'
import { request } from '../手机号注册登录/login_request'

// 邀请人信息
interface RefererInfo {
	user_id: number;
	username?: string;
	nickname?: string;
	phone?: string;
	email?: string;
}

// 绑定邀请人请求
interface BindRefererRequest {
	referer_id: number | string; // 邀请人ID或邀请码
}

// 绑定邀请人响应数据
interface BindRefererData {
	success: boolean;
	referer_info?: RefererInfo;
	message: string;
}

// 通用响应格式
interface ApiResponse<T> {
	code: number;
	data: T;
	message: string;
}

/**
 * 绑定邀请人
 * @param referer_id 邀请人ID（数字）或邀请码（字符串）
 * @returns Promise<BindRefererData>
 */
export const bindReferer = async (referer_id: number | string): Promise<BindRefererData> => {
	const requestData: BindRefererRequest = { referer_id };
	const url = '/invitation/bind-referer/';
	
	const response = await request(buildApiUrl(url), 'POST', requestData);
	const apiResponse = response as ApiResponse<BindRefererData>;
	
	return apiResponse.data;
}
