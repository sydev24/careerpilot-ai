const API_BASE_URL = 'http://localhost:8000';

export async function fetchJobRoles() {
  try {
    const response = await fetch(`${API_BASE_URL}/job-roles`);
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: 'Không thể kết nối đến máy chủ.' }));
      throw new Error(err.detail || 'Lỗi khi tải thông tin vị trí IT.');
    }
    return await response.json();
  } catch (error) {
    console.error('fetchJobRoles error:', error);
    throw error;
  }
}

export async function analyzeCVText(text) {
  try {
    const response = await fetch(`${API_BASE_URL}/analyze-text`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: 'Đã xảy ra lỗi khi phân tích văn bản.' }));
      throw new Error(err.detail || 'Lỗi phân tích CV.');
    }
    return await response.json();
  } catch (error) {
    console.error('analyzeCVText error:', error);
    throw error;
  }
}

export async function uploadCVFile(file) {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/upload-cv`, {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: 'Đã xảy ra lỗi khi tải lên file PDF.' }));
      throw new Error(err.detail || 'Lỗi xử lý file CV.');
    }
    return await response.json();
  } catch (error) {
    console.error('uploadCVFile error:', error);
    throw error;
  }
}
