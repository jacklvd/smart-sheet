/* eslint-disable @typescript-eslint/no-explicit-any */
import axios from 'axios'

const axiosInstance = axios.create({
  withCredentials: false,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json'
  }
})

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001'

const api = {
  summarize: async (data: SummaryRequest): Promise<SummaryResponse> => {
    try {
      const response = await axiosInstance.post(
        `${API_BASE_URL}/api/summarize`,
        data
      )
      return response.data
    } catch (error) {
      console.error('Error summarizing text:', error)
      throw error
    }
  },

  convertMarkdown: async (data: MarkdownRequest): Promise<MarkdownResponse> => {
    try {
      const response = await axiosInstance.post(
        `${API_BASE_URL}/api/markdown`,
        data
      )
      return response.data
    } catch (error) {
      console.error('Error converting markdown:', error)
      throw error
    }
  },

  healthCheck: async (): Promise<any> => {
    try {
      const response = await axiosInstance.get(`${API_BASE_URL}/api/health`)
      return response.data
    } catch (error) {
      console.error('Health check failed:', error)
      throw error
    }
  }
}

export default api
