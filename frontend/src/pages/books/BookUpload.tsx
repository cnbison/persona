// 著作上传页面
import { useState, useRef, ChangeEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, CheckCircle, AlertCircle, X } from 'lucide-react';
import { booksApi } from '../../services/books';

export default function BookUpload() {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [author, setAuthor] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');
  const [uploadedBookId, setUploadedBookId] = useState<string | null>(null);

  // 处理文件选择
  const handleFileSelect = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // 验证文件类型
      const validTypes = ['application/pdf', 'text/plain', 'application/epub+zip'];
      const fileExtension = file.name.split('.').pop()?.toLowerCase();

      if (!validTypes.includes(file.type) && !['pdf', 'txt', 'epub'].includes(fileExtension || '')) {
        alert('请上传PDF、TXT或EPUB格式的文件');
        return;
      }

      // 验证文件大小（最大50MB）
      if (file.size > 50 * 1024 * 1024) {
        alert('文件大小不能超过50MB');
        return;
      }

      setSelectedFile(file);

      // 自动填充标题和作者（从文件名）
      const fileName = file.name.replace(/\.[^/.]+$/, '');
      setTitle(fileName);
    }
  };

  // 处理拖拽
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();

    const file = e.dataTransfer.files[0];
    if (file) {
      // 创建模拟的事件对象
      const mockEvent = {
        target: { files: [file] }
      } as ChangeEvent<HTMLInputElement>;

      handleFileSelect(mockEvent);
    }
  };

  // 上传著作
  const handleUpload = async () => {
    if (!selectedFile) {
      alert('请先选择文件');
      return;
    }

    try {
      setUploading(true);
      setUploadProgress(0);
      setUploadStatus('idle');
      setErrorMessage('');

      // 模拟上传进度
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 10;
        });
      }, 200);

      const response = await booksApi.uploadBook(selectedFile, title || undefined, author || undefined);

      clearInterval(progressInterval);
      setUploadProgress(100);

      setUploadStatus('success');
      setUploadedBookId(response.data.book_id);

      // 3秒后跳转到详情页
      setTimeout(() => {
        navigate(`/books/${response.data.book_id}`);
      }, 3000);

    } catch (err: any) {
      setUploadStatus('error');
      setErrorMessage(err.message || '上传失败，请重试');
      console.error('上传著作失败:', err);
    } finally {
      setUploading(false);
    }
  };

  // 重置表单
  const handleReset = () => {
    setSelectedFile(null);
    setTitle('');
    setAuthor('');
    setUploadProgress(0);
    setUploadStatus('idle');
    setErrorMessage('');
    setUploadedBookId(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="space-y-6">
      {/* 页面头部 */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">上传著作</h1>
        <p className="mt-1 text-sm text-gray-600">
          上传PDF、TXT或EPUB格式的经典著作文件
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 上传区域 */}
        <div className="lg:col-span-2 space-y-6">
          {/* 拖拽上传区域 */}
          {!selectedFile ? (
            <div
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className="mt-2 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md cursor-pointer hover:border-blue-400 transition-colors"
            >
              <div className="space-y-1 text-center">
                <Upload className="mx-auto h-12 w-12 text-gray-400" />
                <div className="flex text-sm text-gray-600">
                  <label
                    htmlFor="file-upload"
                    className="relative cursor-pointer rounded-md font-medium text-blue-600 focus-within:outline-none focus-within:ring-2 focus-within:ring-blue-500 focus-within:ring-offset-2"
                  >
                    <span>点击上传文件</span>
                    <input
                      id="file-upload"
                      name="file-upload"
                      type="file"
                      ref={fileInputRef}
                      className="sr-only"
                      accept=".pdf,.txt,.epub,application/pdf,text/plain,application/epub+zip"
                      onChange={handleFileSelect}
                    />
                  </label>
                </div>
                <p className="text-xs text-gray-500">或拖拽文件到此处</p>
              </div>
              <div className="mt-2 text-center">
                <p className="text-xs text-gray-500">支持PDF、TXT、EPUB格式，最大50MB</p>
              </div>
            </div>
          ) : (
            /* 已选择文件 */
            <div className="mt-2 bg-white border border-gray-300 rounded-md p-4">
              <div className="flex items-start justify-between">
                <div className="flex items-center">
                  <FileText className="h-10 w-10 text-blue-500" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-900">{selectedFile.name}</p>
                    <p className="text-sm text-gray-500">
                      {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                <button
                  onClick={handleReset}
                  className="text-gray-400 hover:text-gray-600"
                  disabled={uploading}
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            </div>
          )}

          {/* 文件信息表单 */}
          {selectedFile && (
            <div className="space-y-4 bg-white border border-gray-300 rounded-md p-6">
              <div>
                <label htmlFor="title" className="block text-sm font-medium text-gray-700">
                  著作标题
                </label>
                <input
                  type="text"
                  id="title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="请输入著作标题"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border"
                  disabled={uploading}
                />
              </div>

              <div>
                <label htmlFor="author" className="block text-sm font-medium text-gray-700">
                  作者
                </label>
                <input
                  type="text"
                  id="author"
                  value={author}
                  onChange={(e) => setAuthor(e.target.value)}
                  placeholder="请输入作者名称"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border"
                  disabled={uploading}
                />
              </div>

              {/* 上传进度 */}
              {uploading && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-700">上传中...</span>
                    <span className="text-gray-500">{uploadProgress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${uploadProgress}%` }}
                    />
                  </div>
                </div>
              )}

              {/* 上传成功 */}
              {uploadStatus === 'success' && (
                <div className="rounded-md bg-green-50 p-4">
                  <div className="flex">
                    <CheckCircle className="h-5 w-5 text-green-400" />
                    <div className="ml-3">
                      <p className="text-sm font-medium text-green-800">上传成功！</p>
                      <p className="text-sm text-green-700 mt-1">
                        正在跳转到著作详情页...
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* 上传失败 */}
              {uploadStatus === 'error' && (
                <div className="rounded-md bg-red-50 p-4">
                  <div className="flex">
                    <AlertCircle className="h-5 w-5 text-red-400" />
                    <div className="ml-3">
                      <p className="text-sm font-medium text-red-800">上传失败</p>
                      <p className="text-sm text-red-700 mt-1">{errorMessage}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* 操作按钮 */}
              <div className="flex gap-3">
                <button
                  onClick={handleUpload}
                  disabled={uploading || uploadStatus === 'success'}
                  className="flex-1 inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-300 disabled:cursor-not-allowed"
                >
                  {uploading ? '上传中...' : uploadStatus === 'success' ? '成功' : '开始上传'}
                </button>
                <button
                  onClick={handleReset}
                  disabled={uploading}
                  className="flex-1 inline-flex justify-center items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                >
                  重置
                </button>
              </div>
            </div>
          )}
        </div>

        {/* 右侧说明 */}
        <div className="space-y-6">
          {/* 支持的格式 */}
          <div className="bg-white border border-gray-300 rounded-md p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">支持的文件格式</h3>
            <ul className="space-y-3">
              <li className="flex items-start">
                <span className="inline-flex items-center rounded-full bg-blue-100 px-2 py-1 text-xs font-medium text-blue-800 mr-2">
                  PDF
                </span>
                <span className="text-sm text-gray-600">推荐格式，解析准确率高</span>
              </li>
              <li className="flex items-start">
                <span className="inline-flex items-center rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-800 mr-2">
                  TXT
                </span>
                <span className="text-sm text-gray-600">纯文本格式，UTF-8编码</span>
              </li>
              <li className="flex items-start">
                <span className="inline-flex items-center rounded-full bg-purple-100 px-2 py-1 text-xs font-medium text-purple-800 mr-2">
                  EPUB
                </span>
                <span className="text-sm text-gray-600">电子书格式，结构完整</span>
              </li>
            </ul>
          </div>

          {/* 上传说明 */}
          <div className="bg-blue-50 border border-blue-200 rounded-md p-6">
            <h3 className="text-lg font-medium text-blue-900 mb-3">上传说明</h3>
            <ul className="space-y-2 text-sm text-blue-800">
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <span>文件大小不超过50MB</span>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <span>系统会自动识别章节结构</span>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <span>提取核心观点和关键词</span>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <span>上传后可构建作者Persona</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
