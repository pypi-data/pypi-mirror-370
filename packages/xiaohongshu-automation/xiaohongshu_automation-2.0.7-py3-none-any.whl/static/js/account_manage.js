let refreshInterval;

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    refreshAllData();
    // 每20分钟自动刷新
    refreshInterval = setInterval(refreshAllData, 1200000);
});

// 添加账号
async function addAccount() {
    const phoneNumber = document.getElementById('phoneNumber').value.trim();
    if (!phoneNumber) {
        showMessage('请输入手机号', 'error');
        return;
    }
    
    try {
        const response = await fetch('/account/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                phone_number: phoneNumber
            })
        });
        
        const data = await response.json();
        if (data.success) {
            showMessage(`账号 ${phoneNumber} 添加成功`, 'success');
            document.getElementById('phoneNumber').value = '';
            refreshAllData();
        } else {
            showMessage(`添加失败: ${data.message}`, 'error');
        }
    } catch (error) {
        showMessage(`添加失败: ${error.message}`, 'error');
    }
}

// 删除账号
async function removeAccount(phoneNumber) {
    if (!confirm(`确定要删除账号 ${phoneNumber} 吗？`)) {
        return;
    }
    
    try {
        const response = await fetch(`/account/remove?phone_number=${phoneNumber}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        if (data.success) {
            showMessage(`账号 ${phoneNumber} 删除成功`, 'success');
            refreshAllData();
        } else {
            showMessage(`删除失败: ${data.message}`, 'error');
        }
    } catch (error) {
        showMessage(`删除失败: ${error.message}`, 'error');
    }
}

// 手动刷新心跳
async function updateHeartbeat(phoneNumber) {
    try {
        const response = await fetch(`/account/heartbeat?phone_number=${phoneNumber}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        if (data.success) {
            showMessage(`账号 ${phoneNumber} 心跳更新成功`, 'success');
            refreshAllData();
        } else {
            showMessage(`心跳更新失败: ${data.message}`, 'error');
        }
    } catch (error) {
        showMessage(`心跳更新失败: ${error.message}`, 'error');
    }
}

// 设为默认账号
async function setDefaultAccount(phoneNumber) {
    try {
        const response = await fetch(`/account/set_default?phone_number=${phoneNumber}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        if (data.success) {
            showMessage(`已设置 ${phoneNumber} 为默认账号`, 'success');
            refreshAllData();
        } else {
            showMessage(`设置默认账号失败: ${data.message}`, 'error');
        }
    } catch (error) {
        showMessage(`设置默认账号失败: ${error.message}`, 'error');
    }
}

// 刷新所有数据
async function refreshAllData() {
    try {
        document.getElementById('accountsContainer').innerHTML = '<div class="loading">正在刷新数据...</div>';
        
        // 并行获取状态、历史数据、根信息、预发布数据和cookies历史记录
        const [statusResponse, historyResponse, rootResponse, prePublishResponse, cookiesHistoryResponse] = await Promise.all([
            fetch('/account/status'),
            fetch('/account/history?limit=5'),
            fetch('/'),
            fetch('/pre_publish/list'),
            fetch('/account/cookies_history')
        ]);
        
        const statusData = await statusResponse.json();
        const historyData = await historyResponse.json();
        const rootData = await rootResponse.json();
        const prePublishData = await prePublishResponse.json();
        const cookiesHistoryData = await cookiesHistoryResponse.json();
        
        if (statusData.success && historyData.success && prePublishData.success) {
            const currentAccount = rootData.account_info?.current_account;
            renderAccounts(statusData.all_accounts_status, historyData.all_accounts_history, currentAccount, prePublishData.all_pre_publishes);
            
            // 同时更新cookies历史记录
            if (cookiesHistoryData.success) {
                renderCookiesHistory(cookiesHistoryData.cookies_files);
            } else {
                // 如果cookies历史记录获取失败，显示默认提示
                const cookiesContainer = document.getElementById('cookiesHistoryContainer');
                if (cookiesContainer) {
                    cookiesContainer.innerHTML = '<div class="loading">点击上方按钮查看历史账号</div>';
                }
            }
        } else {
            document.getElementById('accountsContainer').innerHTML = '<div class="loading">加载失败，请重试</div>';
        }
    } catch (error) {
        document.getElementById('accountsContainer').innerHTML = '<div class="loading">网络错误，请检查连接</div>';
        console.error('刷新数据失败:', error);
    }
}

// 渲染账号卡片
function renderAccounts(statusData, historyData, currentAccount, prePublishData = {}) {
    const container = document.getElementById('accountsContainer');
    
    if (Object.keys(statusData).length === 0) {
        container.innerHTML = '<div class="loading">暂无账号，请先添加账号</div>';
        // 同时更新移动端
        renderMobileAccounts(statusData, historyData, currentAccount, prePublishData);
        return;
    }
    
    // 渲染移动端账号卡片
    renderMobileAccounts(statusData, historyData, currentAccount, prePublishData);
    
    let html = '<div class="accounts-grid">';
    
    for (const [phoneNumber, status] of Object.entries(statusData)) {
        const history = historyData[phoneNumber] || [];
        // 修复：获取最新的3条记录并保持时间逆序（最新的在前）
        const recentHistory = history.slice(-3).reverse();
        const isDefault = phoneNumber === currentAccount;
        const prePublishes = prePublishData[phoneNumber] || [];
        
        html += `
            <div class="account-card">
                <div class="account-header">
                    <div class="account-phone">
                        ${phoneNumber}
                        ${isDefault ? '<span style="color: #667eea; font-size: 0.8em; margin-left: 8px;">【默认】</span>' : ''}
                    </div>
                    <div class="status-badge status-${status.status}">${getStatusText(status.status)}</div>
                    
                    ${prePublishes.length > 0 ? `
                        <div class="idea-bulb" onclick="togglePrePublishList('${phoneNumber}')" title="查看预发布内容">
                            <div class="bulb-icon">💡</div>
                            <div class="idea-count">${prePublishes.length}</div>
                            <div class="idea-bubble">
                                有 ${prePublishes.length} 个新的想法，点击查看
                            </div>
                        </div>
                    ` : ''}
                </div>
                
                <div class="account-stats">
                    <div class="stat-item">
                        <span class="stat-number">${status.publish_count || 0}</span>
                        <div class="stat-label">发布数</div>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">${status.comment_count || 0}</span>
                        <div class="stat-label">评论数</div>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">${status.like_count !== undefined ? status.like_count : 0}</span>
                        <div class="stat-label">点赞数</div>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">${status.collect_count !== undefined ? status.collect_count : 0}</span>
                        <div class="stat-label">收藏数</div>
                    </div>
                </div>
                
                <div style="margin: 15px 0; font-size: 0.9em; color: #666;">
                    <div>浏览器状态: <strong>${getBrowserStatusText(status.browser_status)}</strong></div>
                    <div>自动刷新: <strong>${getRefreshStatusText(status.refresh_status)}</strong></div>
                    <div>最后心跳: ${formatTime(status.last_heartbeat)}</div>
                    <div>Cookie: ${status.cookie_exists ? '✅ 存在' : '❌ 不存在'}</div>
                </div>
                
                <div style="margin: 15px 0;">
                    <button class="btn" onclick="updateHeartbeat('${phoneNumber}')">更新心跳</button>
                    ${!isDefault ? `<button class="btn btn-success" onclick="setDefaultAccount('${phoneNumber}')">设为默认</button>` : ''}
                    <button class="btn" onclick="showAddPrePublishModal('${phoneNumber}')">添加预发布</button>
                    <button class="btn" onclick="showAccountSettingsModal('${phoneNumber}')" style="background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);">⚙️ 设置</button>
                    ${status.refresh_status === 'running' ? 
                        `<button class="btn btn-warning" onclick="stopAutoRefresh('${phoneNumber}')">停止刷新</button>` : 
                        `<button class="btn btn-info" onclick="startAutoRefresh('${phoneNumber}')">启动刷新</button>`
                    }
                    <button class="btn btn-danger" onclick="removeAccount('${phoneNumber}')">删除账号</button>
                </div>
                

                
                ${recentHistory.length > 0 ? `
                    <div class="history-section">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <h4 style="margin: 0; color: #333;">📋 最近活动</h4>
                            <button class="btn-small" onclick="showFullHistoryModal('${phoneNumber}')" style="font-size: 11px; padding: 4px 8px;">
                                查看全部 (${status.publish_count + status.comment_count})
                            </button>
                        </div>
                        ${recentHistory.map(item => `
                            <div class="history-item">
                                <div class="history-time">${item.timestamp}</div>
                                <div class="history-content">
                                    ${getHistoryDisplayText(item)}
                                    ${item.success ? '✅' : '❌'}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                ` : prePublishes.length === 0 ? '<div style="color: #999; text-align: center; padding: 10px;">暂无活动记录</div>' : ''}
            </div>
        `;
    }
    
    html += '</div>';
    container.innerHTML = html;
}

// 获取状态文本
function getStatusText(status) {
    const statusMap = {
        'online': '在线',
        'offline': '离线',
        'error': '错误',
        'timeout': '超时',
        'initialized': '已初始化'
    };
    return statusMap[status] || status;
}

// 获取浏览器状态文本
function getBrowserStatusText(status) {
    const statusMap = {
        'active': '活跃',
        'inactive': '非活跃',
        'not_started': '未启动'
    };
    return statusMap[status] || status;
}

// 获取自动刷新状态文本
function getRefreshStatusText(status) {
    const statusMap = {
        'running': '🟢 运行中',
        'stopped': '🔴 已停止',
        'not_started': '⚪ 未启动'
    };
    return statusMap[status] || status;
}

// 格式化时间
function formatTime(timestamp) {
    const now = new Date().getTime() / 1000;
    const diff = now - timestamp;
    
    if (diff < 60) return '刚刚';
    if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`;
    return `${Math.floor(diff / 86400)}天前`;
}

// 格式化日期时间
function formatDateTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 获取历史记录的显示文本
function getHistoryDisplayText(item) {
    const actionType = item.action_type || item.type;
    
    switch (actionType) {
        case 'publish':
            return `📝 已发布笔记：《${item.title || '无标题'}》`;
        case 'comment':
            return `💬 已发布评论：${item.comment || '无内容'}`;
        case 'like':
            return `👍 已点赞笔记`;
        case 'collect':
            return `⭐ 已收藏笔记`;
        default:
            return `📋 ${actionType || '未知操作'}：${item.comment || item.title || '无内容'}`;
    }
}

// 获取移动端历史记录的显示文本
function getMobileHistoryDisplayText(item) {
    const actionType = item.action_type || item.type;
    
    switch (actionType) {
        case 'publish':
            return `📝 发布：《${item.title || '无标题'}》`;
        case 'comment':
            return `💬 评论：${(item.comment || '无内容').substring(0, 30)}${(item.comment || '').length > 30 ? '...' : ''}`;
        case 'like':
            return `👍 点赞：已为笔记点赞`;
        case 'collect':
            return `⭐ 收藏：已收藏笔记`;
        default:
            return `📋 ${actionType || '未知'}：${(item.comment || item.title || '无内容').substring(0, 30)}`;
    }
}

// 加载cookies历史记录
async function loadCookiesHistory() {
    try {
        document.getElementById('cookiesHistoryContainer').innerHTML = '<div class="loading">正在加载历史账号...</div>';
        
        const response = await fetch('/account/cookies_history');
        const data = await response.json();
        
        if (data.success) {
            renderCookiesHistory(data.cookies_files);
        } else {
            document.getElementById('cookiesHistoryContainer').innerHTML = '<div class="loading">加载失败，请重试</div>';
        }
    } catch (error) {
        document.getElementById('cookiesHistoryContainer').innerHTML = '<div class="loading">网络错误，请检查连接</div>';
        console.error('加载cookies历史失败:', error);
    }
}

// 渲染cookies历史记录
function renderCookiesHistory(cookiesFiles) {
    const container = document.getElementById('cookiesHistoryContainer');
    
    if (cookiesFiles.length === 0) {
        container.innerHTML = '<div class="loading">未发现历史账号cookies文件</div>';
        // 同时更新移动端
        renderMobileCookiesHistory(cookiesFiles);
        return;
    }
    
    // 渲染移动端Cookies历史记录
    renderMobileCookiesHistory(cookiesFiles);
    
    let html = '<div class="cookies-history-grid">';
    
    for (const cookieFile of cookiesFiles) {
        const isActive = cookieFile.is_active;
        const statusClass = isActive ? 'cookie-status-active' : 'cookie-status-inactive';
        const statusText = isActive ? '已激活' : '未激活';
        
        html += `
            <div class="cookie-history-card">
                <div class="cookie-history-header">
                    <div class="cookie-history-phone">
                        ${cookieFile.phone_number === 'default' ? '默认账号' : cookieFile.phone_number}
                    </div>
                    <span class="cookie-status-badge ${statusClass}">${statusText}</span>
                </div>
                
                <div class="cookie-history-info">
                    <div>📂 文件大小: ${cookieFile.file_size_kb} KB</div>
                    <div>🍪 Cookies数: ${cookieFile.cookies_count}</div>
                    <div>🕒 最后修改: ${cookieFile.last_modified_date}</div>
                </div>
                
                <div class="cookie-history-action">
                    ${!isActive ? `
                        <button class="btn" style="width: 100%; margin: 0;" onclick="addAccountFromCookies('${cookieFile.phone_number}')">
                            📥 快速添加
                        </button>
                    ` : `
                        <div class="cookie-history-active-status">
                            ✅ 账号已在使用中
                        </div>
                    `}
                </div>
            </div>
        `;
    }
    
    html += '</div>';
    container.innerHTML = html;
}

// 从cookies历史中添加账号
async function addAccountFromCookies(phoneNumber) {
    try {
        const response = await fetch(`/account/add_from_cookies?phone_number=${phoneNumber}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        if (data.success) {
            showMessage(`从历史记录成功添加账号 ${phoneNumber}`, 'success');
            // 刷新所有数据，包括账号状态和cookies历史记录
            refreshAllData();
        } else {
            showMessage(`添加失败: ${data.message}`, 'error');
        }
    } catch (error) {
        showMessage(`添加失败: ${error.message}`, 'error');
    }
}

// ==================== 预发布相关函数 ====================

// 显示预发布列表模态框
async function togglePrePublishList(phoneNumber) {
    try {
        const response = await fetch(`/pre_publish/list?phone_number=${phoneNumber}`);
        const data = await response.json();
        
        if (data.success) {
            showPrePublishListModal(phoneNumber, data.pre_publishes);
        } else {
            showMessage(`获取预发布列表失败: ${data.message}`, 'error');
        }
    } catch (error) {
        showMessage(`获取预发布列表失败: ${error.message}`, 'error');
    }
}

// 显示预发布列表模态框
function showPrePublishListModal(phoneNumber, prePublishes) {
    // 移除已存在的模态框
    const existingModal = document.getElementById('prePublishListModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // 创建模态框HTML
    const modalHtml = `
        <div id="prePublishListModal" class="pre-publish-modal">
            <div class="pre-publish-card">
                <div class="pre-publish-header">
                    <h3>
                        💡 ${phoneNumber} 的创意想法
                        <span style="font-size: 0.8em; color: #666; font-weight: normal;">(${prePublishes.length} 个)</span>
                    </h3>
                    <button class="pre-publish-close" onclick="closePrePublishListModal()">×</button>
                </div>
                
                <div class="pre-publish-content">
                    ${prePublishes.length > 0 ? prePublishes.map(item => `
                        <div class="pre-publish-item">
                            <div class="pre-publish-item-header">
                                <div>
                                    <div class="pre-publish-item-title">${item.title}</div>
                                    <div class="pre-publish-item-time">创建于 ${formatDateTime(item.created_at)}</div>
                                    ${item.updated_at !== item.created_at ? `<div class="pre-publish-item-time">更新于 ${formatDateTime(item.updated_at)}</div>` : ''}
                                </div>
                            </div>
                            
                            <div class="pre-publish-item-content">${item.content}</div>
                            
                            <div class="pre-publish-item-images">
                                <div class="pre-publish-item-images-header">
                                    <span class="pre-publish-item-images-count">📷 ${item.pic_urls.length} 张图片</span>
                                    ${item.pic_urls.length > 0 ? `
                                        <button class="btn-small" onclick="toggleImagePreview('${item.id}')">
                                            <span id="preview-btn-${item.id}">🔍 预览</span>
                                        </button>
                                    ` : ''}
                                </div>
                                ${item.pic_urls.length > 0 ? `
                                    <div id="image-preview-${item.id}" class="image-preview-container" style="display: none;">
                                        <div class="image-preview-loading">
                                            <div class="loading-spinner"></div>
                                            <div>正在加载图片...</div>
                                        </div>
                                        <div class="image-preview-grid" id="image-grid-${item.id}"></div>
                                    </div>
                                ` : ''}
                            </div>
                            
                            ${item.labels && item.labels.length > 0 ? `
                                <div class="pre-publish-item-labels">
                                    ${item.labels.map(label => `<span class="pre-publish-label">#${label}</span>`).join('')}
                                </div>
                            ` : ''}
                            
                            <div class="pre-publish-item-actions">
                                <button class="btn" onclick="editPrePublish('${item.id}')">编辑</button>
                                <button class="btn btn-success" onclick="publishPrePublishFromModal('${item.id}')">发布</button>
                                <button class="btn btn-danger" onclick="deletePrePublishFromModal('${item.id}')">删除</button>
                            </div>
                        </div>
                    `).join('') : `
                        <div class="pre-publish-empty">
                            <div class="pre-publish-empty-icon">💡</div>
                            <div>还没有创意想法</div>
                            <div style="margin-top: 10px;">
                                <button class="btn" onclick="closePrePublishListModal(); showAddPrePublishModal('${phoneNumber}')">
                                    添加第一个想法
                                </button>
                            </div>
                        </div>
                    `}
                </div>
                
                ${prePublishes.length > 0 ? `
                    <div style="text-align: center; margin-top: 20px; padding-top: 20px; border-top: 1px solid #e1e5e9;">
                        <button class="btn" onclick="closePrePublishListModal(); showAddPrePublishModal('${phoneNumber}')">
                            💡 添加新想法
                        </button>
                    </div>
                ` : ''}
            </div>
        </div>
    `;
    
    // 添加模态框到页面
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // 显示模态框
    const modal = document.getElementById('prePublishListModal');
    setTimeout(() => {
        modal.classList.add('show');
    }, 10);
    
    // 添加点击背景关闭功能
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closePrePublishListModal();
        }
    });
    
    // 预加载所有图片数据
    prePublishes.forEach(item => {
        if (item.pic_urls.length > 0) {
            preloadImagesForPrePublish(item.id, item.pic_urls);
        }
    });
}

// 关闭预发布列表模态框
function closePrePublishListModal() {
    const modal = document.getElementById('prePublishListModal');
    if (modal) {
        modal.classList.remove('show');
        setTimeout(() => {
            modal.remove();
        }, 300);
    }
}

// 切换图片预览
async function toggleImagePreview(prePublishId) {
    const container = document.getElementById(`image-preview-${prePublishId}`);
    const btn = document.getElementById(`preview-btn-${prePublishId}`);
    
    if (container.style.display === 'none') {
        container.style.display = 'block';
        btn.textContent = '🙈 收起';
        await loadImagesForPrePublish(prePublishId);
    } else {
        container.style.display = 'none';
        btn.textContent = '🔍 预览';
    }
}

// 预加载图片数据
async function preloadImagesForPrePublish(prePublishId, picUrls) {
    try {
        const response = await fetch('/pre_publish/download_images', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                pre_publish_id: prePublishId,
                pic_urls: picUrls
            })
        });
        
        if (!response.ok) {
            console.warn(`预加载图片失败: ${prePublishId}`);
        }
    } catch (error) {
        console.warn(`预加载图片错误: ${error.message}`);
    }
}

// 加载并显示图片
async function loadImagesForPrePublish(prePublishId) {
    const loadingElement = document.querySelector(`#image-preview-${prePublishId} .image-preview-loading`);
    const gridElement = document.getElementById(`image-grid-${prePublishId}`);
    
    try {
        loadingElement.style.display = 'block';
        gridElement.style.display = 'none';
        
        const response = await fetch(`/pre_publish/get_images?pre_publish_id=${prePublishId}`);
        const data = await response.json();
        
        if (data.success && data.images) {
            let imagesHtml = '';
            data.images.forEach((imageInfo, index) => {
                const imageUrl = imageInfo.local_path ? `/pre_publish/image/${prePublishId}/${encodeURIComponent(imageInfo.filename)}` : imageInfo.original_url;
                const status = imageInfo.downloaded ? '✅' : '⚠️';
                
                imagesHtml += `
                    <div class="image-preview-item">
                        <div class="image-preview-wrapper">
                            <img src="${imageUrl}" 
                                 alt="预发布图片 ${index + 1}" 
                                 onclick="showImageFullscreen('${imageUrl}')"
                                 onerror="handleImageError(this, '${imageInfo.original_url}')"
                                 loading="lazy">
                            <div class="image-preview-overlay">
                                <button class="image-fullscreen-btn" onclick="showImageFullscreen('${imageUrl}')">🔍</button>
                                <div class="image-status">${status}</div>
                            </div>
                        </div>
                        <div class="image-preview-info">
                            <small>${imageInfo.filename}</small>
                            ${imageInfo.file_size ? `<small>${formatFileSize(imageInfo.file_size)}</small>` : ''}
                        </div>
                    </div>
                `;
            });
            
            gridElement.innerHTML = imagesHtml;
            gridElement.style.display = 'grid';
        } else {
            gridElement.innerHTML = '<div class="image-preview-error">加载图片失败</div>';
            gridElement.style.display = 'block';
        }
    } catch (error) {
        gridElement.innerHTML = '<div class="image-preview-error">网络错误，无法加载图片</div>';
        gridElement.style.display = 'block';
        console.error('加载图片失败:', error);
    } finally {
        loadingElement.style.display = 'none';
    }
}

// 处理图片加载错误
function handleImageError(img, originalUrl) {
    img.src = originalUrl;
    img.onerror = function() {
        img.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICAgIDxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjZjVmNWY1Ii8+CiAgICA8dGV4dCB4PSI1MCUiIHk9IjUwJSIgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZmlsbD0iIzk5OTk5OSIgZm9udC1mYW1pbHk9IkFyaWFsLCBzYW5zLXNlcmlmIiBmb250LXNpemU9IjE0cHgiPuWbvueJh+WKoOi9veWkseai6TwvdGV4dD4KPC9zdmc+';
    };
}

// 显示图片全屏预览
function showImageFullscreen(imageUrl) {
    const fullscreenHtml = `
        <div id="imageFullscreenModal" style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.9);
            z-index: 2000;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
        " onclick="closeImageFullscreen()">
            <div style="
                max-width: 90%;
                max-height: 90%;
                display: flex;
                align-items: center;
                justify-content: center;
            " onclick="event.stopPropagation()">
                <img src="${imageUrl}" style="
                    max-width: 100%;
                    max-height: 100%;
                    border-radius: 8px;
                    box-shadow: 0 0 20px rgba(255,255,255,0.3);
                ">
            </div>
            <button style="
                position: absolute;
                top: 20px;
                right: 20px;
                background: rgba(255,255,255,0.2);
                border: none;
                color: white;
                font-size: 24px;
                width: 40px;
                height: 40px;
                border-radius: 50%;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
            " onclick="closeImageFullscreen()">×</button>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', fullscreenHtml);
}

// 关闭图片全屏预览
function closeImageFullscreen() {
    const modal = document.getElementById('imageFullscreenModal');
    if (modal) {
        modal.remove();
    }
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// 从模态框中发布预发布内容
async function publishPrePublishFromModal(prePublishId) {
    const result = await publishPrePublish(prePublishId);
    // 发布成功后清理图片并关闭模态框
    if (result !== false) {
        await cleanupPrePublishImages(prePublishId);
        closePrePublishListModal();
    }
}

// 从模态框中删除预发布内容
async function deletePrePublishFromModal(prePublishId) {
    const result = await deletePrePublish(prePublishId);
    // 删除成功后清理图片并关闭模态框
    if (result !== false) {
        await cleanupPrePublishImages(prePublishId);
        closePrePublishListModal();
    }
}

// 显示添加预发布模态框
function showAddPrePublishModal(phoneNumber) {
    showPrePublishModal(phoneNumber, null, '添加预发布内容');
}

// 编辑预发布内容
async function editPrePublish(prePublishId) {
    try {
        const response = await fetch(`/pre_publish/get?pre_publish_id=${prePublishId}`);
        const data = await response.json();
        
        if (data.success) {
            showPrePublishModal(data.phone_number, data.pre_publish, '编辑预发布内容');
        } else {
            showMessage(`获取预发布内容失败: ${data.message}`, 'error');
        }
    } catch (error) {
        showMessage(`获取预发布内容失败: ${error.message}`, 'error');
    }
}

// 发布预发布内容
async function publishPrePublish(prePublishId) {
    if (!confirm('确定要发布这个内容吗？发布后将从预发布列表中移除。')) {
        return false;
    }
    
    try {
        // 首先检查最近活动状态
        showMessage('正在检查账号活动状态...', 'info');
        
        const checkResponse = await fetch(`/pre_publish/check_activity?pre_publish_id=${prePublishId}`, {
            method: 'GET'
        });
        
        const checkData = await checkResponse.json();
        
        if (checkData.success && checkData.has_recent_activity) {
            // 有最近活动，显示详细的确认对话框
            const message = `⚠️ 检测到账号 ${checkData.phone_number} 最近有活动：\n\n` +
                          `• 最后活动时间: ${checkData.last_activity_time}\n` +
                          `• 活动类型: ${checkData.last_activity_type}\n` +
                          `• 操作间隔: ${checkData.interval_seconds} 秒\n\n` +
                          `为了避免频繁操作被限制，建议稍后再发布。\n\n` +
                          `是否仍要继续发布？`;
            
            if (!confirm(message)) {
                showMessage('已取消发布，建议稍后再试', 'info');
                return false;
            }
            
            // 用户选择继续发布，显示额外的确认
            if (!confirm('⚠️ 最后确认：您确定要在有最近活动的情况下继续发布吗？这可能增加账号风险。')) {
                showMessage('已取消发布', 'info');
                return false;
            }
        }
        
        // 进行实际发布
        showMessage('正在发布内容...', 'info');
        
        const response = await fetch(`/pre_publish/publish?pre_publish_id=${prePublishId}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        if (data.success) {
            showMessage(`发布成功！账号: ${data.phone_number}`, 'success');
            refreshAllData();
            return true;
        } else {
            showMessage(`发布失败: ${data.message}`, 'error');
            return false;
        }
    } catch (error) {
        showMessage(`发布失败: ${error.message}`, 'error');
        return false;
    }
}

// 删除预发布内容
async function deletePrePublish(prePublishId) {
    if (!confirm('确定要删除这个预发布内容吗？')) {
        return false;
    }
    
    try {
        const response = await fetch(`/pre_publish/delete?pre_publish_id=${prePublishId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        if (data.success) {
            showMessage(`删除成功！账号: ${data.phone_number}`, 'success');
            refreshAllData();
            return true;
        } else {
            showMessage(`删除失败: ${data.message}`, 'error');
            return false;
        }
    } catch (error) {
        showMessage(`删除失败: ${error.message}`, 'error');
        return false;
    }
}

// 显示预发布模态框
function showPrePublishModal(phoneNumber, prePublishData = null, title = '预发布内容') {
    const isEdit = prePublishData !== null;
    
    // 移除已存在的模态框
    const existingModal = document.getElementById('prePublishModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // 创建模态框HTML
    const modalHtml = `
        <div id="prePublishModal" style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        ">
            <div style="
                background: white;
                border-radius: 15px;
                padding: 30px;
                max-width: 600px;
                width: 100%;
                max-height: 90vh;
                overflow-y: auto;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            ">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <h3 style="margin: 0; color: #333;">${title}</h3>
                    <button onclick="closePrePublishModal()" style="
                        background: none;
                        border: none;
                        font-size: 24px;
                        cursor: pointer;
                        color: #666;
                    ">×</button>
                </div>
                
                <form id="prePublishForm">
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #555;">账号</label>
                        <input type="text" value="${phoneNumber}" disabled style="
                            width: 100%;
                            padding: 12px 16px;
                            border: 2px solid #e1e5e9;
                            border-radius: 8px;
                            font-size: 16px;
                            background: #f8f9fa;
                        ">
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #555;">标题 *</label>
                        <input type="text" id="prePublishTitle" required style="
                            width: 100%;
                            padding: 12px 16px;
                            border: 2px solid #e1e5e9;
                            border-radius: 8px;
                            font-size: 16px;
                            transition: border-color 0.3s ease;
                        " value="${prePublishData ? prePublishData.title : ''}" placeholder="请输入标题">
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #555;">内容 *</label>
                        <textarea id="prePublishContent" required style="
                            width: 100%;
                            padding: 12px 16px;
                            border: 2px solid #e1e5e9;
                            border-radius: 8px;
                            font-size: 16px;
                            transition: border-color 0.3s ease;
                            min-height: 120px;
                            resize: vertical;
                        " placeholder="请输入内容">${prePublishData ? prePublishData.content : ''}</textarea>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #555;">图片链接 *</label>
                        <textarea id="prePublishPicUrls" required style="
                            width: 100%;
                            padding: 12px 16px;
                            border: 2px solid #e1e5e9;
                            border-radius: 8px;
                            font-size: 16px;
                            transition: border-color 0.3s ease;
                            min-height: 80px;
                            resize: vertical;
                        " placeholder="请输入图片链接，每行一个">${prePublishData ? prePublishData.pic_urls.join('\\n') : ''}</textarea>
                        <small style="color: #666; font-size: 14px;">每行输入一个图片链接</small>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #555;">标签</label>
                        <input type="text" id="prePublishLabels" style="
                            width: 100%;
                            padding: 12px 16px;
                            border: 2px solid #e1e5e9;
                            border-radius: 8px;
                            font-size: 16px;
                            transition: border-color 0.3s ease;
                        " value="${prePublishData ? (prePublishData.labels || []).join(', ') : ''}" placeholder="请输入标签，用逗号分隔">
                        <small style="color: #666; font-size: 14px;">多个标签用逗号分隔</small>
                    </div>
                    
                    <div style="text-align: right; margin-top: 30px;">
                        <button type="button" onclick="closePrePublishModal()" style="
                            background: #6c757d;
                            color: white;
                            border: none;
                            padding: 12px 24px;
                            border-radius: 8px;
                            cursor: pointer;
                            font-size: 16px;
                            font-weight: 600;
                            margin-right: 10px;
                        ">取消</button>
                        <button type="submit" style="
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            border: none;
                            padding: 12px 24px;
                            border-radius: 8px;
                            cursor: pointer;
                            font-size: 16px;
                            font-weight: 600;
                        ">${isEdit ? '更新' : '添加'}</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    
    // 添加模态框到页面
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // 添加表单提交事件
    document.getElementById('prePublishForm').addEventListener('submit', function(e) {
        e.preventDefault();
        if (isEdit) {
            updatePrePublish(prePublishData.id);
        } else {
            addPrePublish(phoneNumber);
        }
    });
    
    // 聚焦到标题输入框
    document.getElementById('prePublishTitle').focus();
}

// 关闭预发布模态框
function closePrePublishModal() {
    const modal = document.getElementById('prePublishModal');
    if (modal) {
        modal.remove();
    }
}

// 添加预发布内容
async function addPrePublish(phoneNumber) {
    const title = document.getElementById('prePublishTitle').value.trim();
    const content = document.getElementById('prePublishContent').value.trim();
    const picUrlsText = document.getElementById('prePublishPicUrls').value.trim();
    const labelsText = document.getElementById('prePublishLabels').value.trim();
    
    if (!title || !content || !picUrlsText) {
        showMessage('请填写标题、内容和图片链接', 'error');
        return;
    }
    
    // 处理图片链接和标签
    const pic_urls = picUrlsText.split('\\n').map(url => url.trim()).filter(url => url);
    const labels = labelsText ? labelsText.split(',').map(label => label.trim()).filter(label => label) : [];
    
    try {
        const response = await fetch('/pre_publish/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                phone_number: phoneNumber,
                title: title,
                content: content,
                pic_urls: pic_urls,
                labels: labels
            })
        });
        
        const data = await response.json();
        if (data.success) {
            showMessage(`预发布内容添加成功！账号: ${data.phone_number}`, 'success');
            closePrePublishModal();
            refreshAllData();
        } else {
            showMessage(`添加失败: ${data.message}`, 'error');
        }
    } catch (error) {
        showMessage(`添加失败: ${error.message}`, 'error');
    }
}

// 更新预发布内容
async function updatePrePublish(prePublishId) {
    const title = document.getElementById('prePublishTitle').value.trim();
    const content = document.getElementById('prePublishContent').value.trim();
    const picUrlsText = document.getElementById('prePublishPicUrls').value.trim();
    const labelsText = document.getElementById('prePublishLabels').value.trim();
    
    if (!title || !content || !picUrlsText) {
        showMessage('请填写标题、内容和图片链接', 'error');
        return;
    }
    
    // 处理图片链接和标签
    const pic_urls = picUrlsText.split('\\n').map(url => url.trim()).filter(url => url);
    const labels = labelsText ? labelsText.split(',').map(label => label.trim()).filter(label => label) : [];
    
    try {
        const response = await fetch('/pre_publish/update', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                pre_publish_id: prePublishId,
                title: title,
                content: content,
                pic_urls: pic_urls,
                labels: labels
            })
        });
        
        const data = await response.json();
        if (data.success) {
            showMessage(`预发布内容更新成功！账号: ${data.phone_number}`, 'success');
            closePrePublishModal();
            refreshAllData();
        } else {
            showMessage(`更新失败: ${data.message}`, 'error');
        }
    } catch (error) {
        showMessage(`更新失败: ${error.message}`, 'error');
    }
}

// 显示消息
function showMessage(text, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = text;
    
    document.querySelector('.main-content').insertBefore(messageDiv, document.querySelector('.section'));
    
    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
}

// ==================== 自动刷新控制函数 ====================

// 停止自动刷新任务
async function stopAutoRefresh(phoneNumber) {
    try {
        const response = await fetch(`/account/stop_refresh?phone_number=${phoneNumber}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        if (data.success) {
            showMessage(`账号 ${phoneNumber} 自动刷新任务已停止`, 'success');
            refreshAllData();
        } else {
            showMessage(`停止自动刷新失败: ${data.message}`, 'error');
        }
    } catch (error) {
        showMessage(`停止自动刷新失败: ${error.message}`, 'error');
    }
}

// 启动自动刷新任务
async function startAutoRefresh(phoneNumber) {
    try {
        const response = await fetch(`/account/start_refresh?phone_number=${phoneNumber}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        if (data.success) {
            showMessage(`账号 ${phoneNumber} 自动刷新任务已启动`, 'success');
            refreshAllData();
        } else {
            showMessage(`启动自动刷新失败: ${data.message}`, 'error');
        }
    } catch (error) {
        showMessage(`启动自动刷新失败: ${error.message}`, 'error');
    }
}

// 清理预发布图片
async function cleanupPrePublishImages(prePublishId) {
    try {
        await fetch(`/pre_publish/cleanup_images?pre_publish_id=${prePublishId}`, {
            method: 'DELETE'
        });
    } catch (error) {
        console.warn('清理图片失败:', error);
    }
}

// ==================== 账号设置相关函数 ====================

// 显示账号设置模态框
async function showAccountSettingsModal(phoneNumber) {
    // 首先获取当前代理配置
    let currentProxy = null;
    try {
        const response = await fetch(`/account/get_proxy?phone_number=${phoneNumber}`);
        const data = await response.json();
        if (data.success) {
            currentProxy = data.proxy_config;
        }
    } catch (error) {
        console.warn('获取当前代理配置失败:', error);
    }
    
    // 移除已存在的模态框
    const existingModal = document.getElementById('accountSettingsModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // 创建模态框HTML
    const modalHtml = `
        <div id="accountSettingsModal" class="pre-publish-modal">
            <div class="pre-publish-card" style="max-width: 650px;">
                <div class="pre-publish-header">
                    <h3>⚙️ 账号设置 - ${phoneNumber}</h3>
                    <button class="pre-publish-close" onclick="closeAccountSettingsModal()">×</button>
                </div>
                
                <div class="pre-publish-content">
                    <!-- 当前代理状态 -->
                    <div class="settings-section">
                        <h4 style="color: #333; margin-bottom: 15px; display: flex; align-items: center;">
                            🌐 代理设置
                            <button class="btn-small" onclick="refreshProxyStatus('${phoneNumber}')" style="margin-left: 10px; font-size: 12px;">
                                🔄 刷新状态
                            </button>
                        </h4>
                        
                        <div id="proxyStatusContainer" class="proxy-status-container">
                            <div class="loading">正在获取代理状态...</div>
                        </div>
                    </div>
                    
                    <!-- 代理历史记录 -->
                    <div class="settings-section" id="proxyHistorySection">
                        <h4 style="color: #333; margin-bottom: 15px;">📚 代理历史记录</h4>
                        <div id="proxyHistoryContainer">
                            <div class="loading">正在加载历史记录...</div>
                        </div>
                    </div>
                    
                    <!-- 代理设置表单 -->
                    <div class="settings-section">
                        <h4 style="color: #333; margin-bottom: 15px;">📝 设置新代理</h4>
                        
                        <form id="proxySettingsForm">
                            <div class="form-row">
                                <div class="form-group">
                                    <label>代理类型</label>
                                    <select id="proxyType" style="
                                        width: 100%;
                                        padding: 8px 12px;
                                        border: 2px solid #e1e5e9;
                                        border-radius: 6px;
                                        font-size: 14px;
                                    ">
                                        <option value="">无代理</option>
                                        <option value="http">HTTP</option>
                                        <option value="https">HTTPS</option>
                                        <option value="socks4">SOCKS4</option>
                                        <option value="socks5">SOCKS5</option>
                                    </select>
                                </div>
                            </div>
                            
                            <div class="form-row" id="proxyDetailsRow" style="display: none;">
                                <div class="form-group">
                                    <label>服务器地址</label>
                                    <input type="text" id="proxyHost" placeholder="例如：127.0.0.1" style="
                                        width: 100%;
                                        padding: 8px 12px;
                                        border: 2px solid #e1e5e9;
                                        border-radius: 6px;
                                        font-size: 14px;
                                    ">
                                </div>
                                <div class="form-group">
                                    <label>端口</label>
                                    <input type="number" id="proxyPort" placeholder="例如：8080" min="1" max="65535" style="
                                        width: 100%;
                                        padding: 8px 12px;
                                        border: 2px solid #e1e5e9;
                                        border-radius: 6px;
                                        font-size: 14px;
                                    ">
                                </div>
                            </div>
                            
                            <div class="form-row" id="proxyAuthRow" style="display: none;">
                                <div class="form-group">
                                    <label>用户名（可选）</label>
                                    <input type="text" id="proxyUsername" placeholder="代理用户名" style="
                                        width: 100%;
                                        padding: 8px 12px;
                                        border: 2px solid #e1e5e9;
                                        border-radius: 6px;
                                        font-size: 14px;
                                    ">
                                </div>
                                <div class="form-group">
                                    <label>密码（可选）</label>
                                    <input type="password" id="proxyPassword" placeholder="代理密码" style="
                                        width: 100%;
                                        padding: 8px 12px;
                                        border: 2px solid #e1e5e9;
                                        border-radius: 6px;
                                        font-size: 14px;
                                    ">
                                </div>
                            </div>
                            
                            <div class="form-actions" style="text-align: center; margin-top: 20px;">
                                <button type="button" onclick="applyProxySettings('${phoneNumber}')" class="btn" style="
                                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                    color: white;
                                    margin-right: 10px;
                                ">🔧 应用代理设置</button>
                                <button type="button" onclick="clearProxySettings('${phoneNumber}')" class="btn" style="
                                    background: #6c757d;
                                    color: white;
                                ">🚫 清除代理</button>
                            </div>
                        </form>
                    </div>
                    
                    <!-- 浏览器控制 -->
                    <div class="settings-section">
                        <h4 style="color: #333; margin-bottom: 15px;">🌐 浏览器控制</h4>
                        <div class="browser-controls">
                            <button class="btn" onclick="restartBrowser('${phoneNumber}')" style="
                                background: linear-gradient(135deg, #FF6B6B 0%, #EE5A52 100%);
                                color: white;
                                margin-right: 10px;
                            ">🔄 重启浏览器</button>
                            <button class="btn" onclick="testProxyConnection('${phoneNumber}')" style="
                                background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%);
                                color: white;
                            ">🔍 测试连接</button>
                        </div>
                        <div style="margin-top: 10px; font-size: 13px; color: #666;">
                            ⚠️ 重启浏览器将应用新的代理设置，并重新加载所有页面
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // 添加模态框到页面
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // 显示模态框
    const modal = document.getElementById('accountSettingsModal');
    setTimeout(() => {
        modal.classList.add('show');
    }, 10);
    
    // 添加点击背景关闭功能
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeAccountSettingsModal();
        }
    });
    
    // 设置代理类型切换事件
    document.getElementById('proxyType').addEventListener('change', function() {
        const proxyType = this.value;
        const detailsRow = document.getElementById('proxyDetailsRow');
        const authRow = document.getElementById('proxyAuthRow');
        
        if (proxyType) {
            detailsRow.style.display = 'block';
            authRow.style.display = 'block';
        } else {
            detailsRow.style.display = 'none';
            authRow.style.display = 'none';
        }
    });
    
    // 加载当前代理状态
    await refreshProxyStatus(phoneNumber);
    
    // 如果有当前代理配置，则填充表单
    if (currentProxy) {
        fillProxyForm(currentProxy);
    }
    
    // 加载代理历史记录
    await loadProxyHistory(phoneNumber);
}

// 关闭账号设置模态框
function closeAccountSettingsModal() {
    const modal = document.getElementById('accountSettingsModal');
    if (modal) {
        modal.classList.remove('show');
        setTimeout(() => {
            modal.remove();
        }, 300);
    }
}

// 刷新代理状态
async function refreshProxyStatus(phoneNumber) {
    const container = document.getElementById('proxyStatusContainer');
    if (!container) return;
    
    container.innerHTML = '<div class="loading">正在获取代理状态...</div>';
    
    try {
        const response = await fetch(`/account/get_proxy?phone_number=${phoneNumber}`);
        const data = await response.json();
        
        if (data.success) {
            const proxy = data.proxy_config;
            let statusHtml = '';
            
            if (proxy && proxy.type) {
                // 处理连接状态 - 可能是对象或字符串
                let statusText = '未知';
                let statusColor = '#666';
                
                if (typeof data.connection_status === 'object' && data.connection_status !== null) {
                    // 如果是对象，提取有用的信息
                    if (data.connection_status.connected) {
                        statusText = `✅ 连接正常 (IP: ${data.connection_status.ip || '未知'}, 延迟: ${data.connection_status.latency || 0}ms)`;
                        statusColor = '#28a745';
                    } else {
                        statusText = `❌ 连接失败 (${data.connection_status.message || data.connection_status.error || '未知错误'})`;
                        statusColor = '#dc3545';
                    }
                } else if (typeof data.connection_status === 'string') {
                    // 如果是字符串，直接使用
                    statusText = data.connection_status;
                    if (statusText.includes('成功') || statusText.includes('正常')) {
                        statusColor = '#28a745';
                    } else if (statusText.includes('失败') || statusText.includes('错误')) {
                        statusColor = '#dc3545';
                    }
                }
                
                statusHtml = `
                    <div class="proxy-status-card proxy-enabled">
                        <div class="proxy-status-header">
                            <span class="proxy-status-icon">🟢</span>
                            <span class="proxy-status-text">代理已启用</span>
                        </div>
                        <div class="proxy-details">
                            <div><strong>类型:</strong> ${proxy.type.toUpperCase()}</div>
                            <div><strong>服务器:</strong> ${proxy.host}:${proxy.port}</div>
                            ${proxy.username ? `<div><strong>用户名:</strong> ${proxy.username}</div>` : ''}
                            <div><strong>状态:</strong> <span style="color: ${statusColor};">${statusText}</span></div>
                        </div>
                    </div>
                `;
            } else {
                statusHtml = `
                    <div class="proxy-status-card proxy-disabled">
                        <div class="proxy-status-header">
                            <span class="proxy-status-icon">🔴</span>
                            <span class="proxy-status-text">未设置代理</span>
                        </div>
                        <div class="proxy-details">
                            <div>当前使用直连网络访问</div>
                        </div>
                    </div>
                `;
            }
            
            container.innerHTML = statusHtml;
        } else {
            container.innerHTML = `<div class="proxy-status-error">获取代理状态失败: ${data.message}</div>`;
        }
    } catch (error) {
        container.innerHTML = `<div class="proxy-status-error">网络错误: ${error.message}</div>`;
    }
}

// 填充代理表单
function fillProxyForm(proxyConfig) {
    if (!proxyConfig) return;
    
    document.getElementById('proxyType').value = proxyConfig.type || '';
    document.getElementById('proxyHost').value = proxyConfig.host || '';
    document.getElementById('proxyPort').value = proxyConfig.port || '';
    document.getElementById('proxyUsername').value = proxyConfig.username || '';
    document.getElementById('proxyPassword').value = proxyConfig.password || '';
    
    // 触发类型切换事件
    document.getElementById('proxyType').dispatchEvent(new Event('change'));
}

// 应用代理设置
async function applyProxySettings(phoneNumber) {
    const proxyType = document.getElementById('proxyType').value;
    const proxyHost = document.getElementById('proxyHost').value.trim();
    const proxyPort = document.getElementById('proxyPort').value.trim();
    const proxyUsername = document.getElementById('proxyUsername').value.trim();
    const proxyPassword = document.getElementById('proxyPassword').value.trim();
    
    // 验证输入
    if (proxyType && (!proxyHost || !proxyPort)) {
        showMessage('请填写完整的代理服务器地址和端口', 'error');
        return;
    }
    
    const proxyConfig = {
        type: proxyType || null,
        host: proxyHost || null,
        port: proxyPort ? parseInt(proxyPort) : null,
        username: proxyUsername || null,
        password: proxyPassword || null
    };
    
    try {
        showMessage('正在应用代理设置...', 'info');
        
        const response = await fetch('/account/set_proxy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                phone_number: phoneNumber,
                proxy_config: proxyConfig
            })
        });
        
        const data = await response.json();
        if (data.success) {
            showMessage(`代理设置已应用！账号: ${phoneNumber}`, 'success');
            // 刷新代理状态和历史记录
            await refreshProxyStatus(phoneNumber);
            await loadProxyHistory(phoneNumber);
        } else {
            showMessage(`应用代理设置失败: ${data.message}`, 'error');
        }
    } catch (error) {
        showMessage(`应用代理设置失败: ${error.message}`, 'error');
    }
}

// 清除代理设置
async function clearProxySettings(phoneNumber) {
    if (!confirm('确定要清除代理设置吗？')) {
        return;
    }
    
    try {
        showMessage('正在清除代理设置...', 'info');
        
        const response = await fetch('/account/clear_proxy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                phone_number: phoneNumber
            })
        });
        
        const data = await response.json();
        if (data.success) {
            showMessage(`代理设置已清除！账号: ${phoneNumber}`, 'success');
            
            // 清空表单
            document.getElementById('proxyType').value = '';
            document.getElementById('proxyHost').value = '';
            document.getElementById('proxyPort').value = '';
            document.getElementById('proxyUsername').value = '';
            document.getElementById('proxyPassword').value = '';
            document.getElementById('proxyType').dispatchEvent(new Event('change'));
            
            await refreshProxyStatus(phoneNumber);
        } else {
            showMessage(`清除代理设置失败: ${data.message}`, 'error');
        }
    } catch (error) {
        showMessage(`清除代理设置失败: ${error.message}`, 'error');
    }
}

// 重启浏览器
async function restartBrowser(phoneNumber) {
    if (!confirm('确定要重启浏览器吗？这将关闭当前浏览器实例并重新启动，可能会丢失未保存的数据。')) {
        return;
    }
    
    try {
        showMessage('正在重启浏览器...', 'info');
        
        const response = await fetch('/account/restart_browser', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                phone_number: phoneNumber
            })
        });
        
        const data = await response.json();
        if (data.success) {
            showMessage(`浏览器重启成功！账号: ${phoneNumber}`, 'success');
            closeAccountSettingsModal();
            refreshAllData();
        } else {
            showMessage(`重启浏览器失败: ${data.message}`, 'error');
        }
    } catch (error) {
        showMessage(`重启浏览器失败: ${error.message}`, 'error');
    }
}

// 测试代理连接
async function testProxyConnection(phoneNumber) {
    try {
        showMessage('正在测试代理连接...', 'info');
        
        const response = await fetch('/account/test_proxy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                phone_number: phoneNumber
            })
        });
        
        const data = await response.json();
        if (data.success) {
            const result = data.test_result;
            if (result.connected) {
                showMessage(`代理连接测试成功！IP: ${result.ip || '未知'}, 延迟: ${result.latency || '未知'}ms`, 'success');
            } else {
                showMessage(`代理连接测试失败: ${result.error || '连接超时'}`, 'error');
            }
        } else {
            showMessage(`测试代理连接失败: ${data.message}`, 'error');
        }
    } catch (error) {
        showMessage(`测试代理连接失败: ${error.message}`, 'error');
    }
}

// 页面卸载时清理定时器
window.addEventListener('beforeunload', function() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
});

// ==================== 代理历史管理函数 ====================

// 加载代理历史记录
async function loadProxyHistory(phoneNumber) {
    try {
        const response = await fetch('/account/get_proxy_history');
        const data = await response.json();
        
        if (data.success) {
            renderProxyHistory(data.proxy_history, phoneNumber);
        } else {
            document.getElementById('proxyHistoryContainer').innerHTML = `
                <div class="proxy-status-error">
                    获取历史记录失败: ${data.message}
                </div>
            `;
        }
    } catch (error) {
        console.error('加载代理历史失败:', error);
        document.getElementById('proxyHistoryContainer').innerHTML = `
            <div class="proxy-status-error">
                网络错误，无法加载历史记录
            </div>
        `;
    }
}

// 渲染代理历史记录
function renderProxyHistory(proxyHistory, phoneNumber) {
    const container = document.getElementById('proxyHistoryContainer');
    
    if (!proxyHistory || proxyHistory.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; color: #666; padding: 20px; font-style: italic;">
                暂无代理历史记录
            </div>
        `;
        return;
    }
    
    let html = `
        <div style="margin-bottom: 10px; font-size: 13px; color: #666;">
            共找到 ${proxyHistory.length} 条历史记录，按使用时间排序
        </div>
        <div style="max-height: 300px; overflow-y: auto; border: 1px solid #e1e5e9; border-radius: 8px;">
    `;
    
    proxyHistory.forEach((proxy, index) => {
        const config = proxy.config;
        const lastUsed = new Date(proxy.last_used).toLocaleString();
        const useCount = proxy.use_count || 1;
        
        html += `
            <div class="proxy-history-item" style="
                padding: 15px;
                border-bottom: ${index < proxyHistory.length - 1 ? '1px solid #f1f3f4' : 'none'};
                transition: background-color 0.3s ease;
                cursor: pointer;
                position: relative;
            " onmouseover="this.style.backgroundColor='#f8f9fa'" onmouseout="this.style.backgroundColor='white'">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div style="flex: 1;">
                        <div style="font-weight: 600; color: #333; margin-bottom: 5px;">
                            ${proxy.name}
                            <span style="
                                background: #667eea;
                                color: white;
                                padding: 2px 6px;
                                border-radius: 10px;
                                font-size: 11px;
                                margin-left: 8px;
                            ">${config.type.toUpperCase()}</span>
                        </div>
                        <div style="font-size: 13px; color: #666; margin-bottom: 8px;">
                            <div>服务器: ${config.host}:${config.port}</div>
                            ${config.username ? `<div>认证: ${config.username}</div>` : ''}
                            <div>使用次数: ${useCount} 次</div>
                            <div>最后使用: ${lastUsed}</div>
                        </div>
                        <div style="display: flex; gap: 8px;">
                            <button class="btn-small" onclick="applyProxyFromHistory('${proxy.id}', '${phoneNumber}')" style="
                                background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                                color: white;
                                font-size: 12px;
                                padding: 4px 10px;
                            ">📋 应用此代理</button>
                            <button class="btn-small" onclick="fillProxyFormFromHistory('${proxy.id}')" style="
                                background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
                                color: white;
                                font-size: 12px;
                                padding: 4px 10px;
                            ">✏️ 填入表单</button>
                        </div>
                    </div>
                    <div style="margin-left: 10px;">
                        <button class="btn-small" onclick="deleteProxyFromHistory('${proxy.id}', '${phoneNumber}')" style="
                            background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
                            color: white;
                            font-size: 11px;
                            padding: 4px 8px;
                        ">🗑️</button>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

// 从历史记录直接应用代理配置
async function applyProxyFromHistory(proxyId, phoneNumber) {
    try {
        // 先获取代理历史记录
        const response = await fetch('/account/get_proxy_history');
        const data = await response.json();
        
        if (!data.success) {
            showMessage('获取代理历史失败', 'error');
            return;
        }
        
        // 找到对应的代理配置
        const proxy = data.proxy_history.find(p => p.id === proxyId);
        if (!proxy) {
            showMessage('未找到指定的代理配置', 'error');
            return;
        }
        
        // 应用代理配置
        const setResponse = await fetch('/account/set_proxy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                phone_number: phoneNumber,
                proxy_config: proxy.config
            })
        });
        
        const setData = await setResponse.json();
        if (setData.success) {
            showMessage(`代理 ${proxy.name} 应用成功`, 'success');
            // 刷新代理状态和历史记录
            await refreshProxyStatus(phoneNumber);
            await loadProxyHistory(phoneNumber);
        } else {
            showMessage(`代理应用失败: ${setData.message}`, 'error');
        }
    } catch (error) {
        console.error('应用代理失败:', error);
        showMessage('应用代理失败: 网络错误', 'error');
    }
}

// 从历史记录填入表单
async function fillProxyFormFromHistory(proxyId) {
    try {
        // 获取代理历史记录
        const response = await fetch('/account/get_proxy_history');
        const data = await response.json();
        
        if (!data.success) {
            showMessage('获取代理历史失败', 'error');
            return;
        }
        
        // 找到对应的代理配置
        const proxy = data.proxy_history.find(p => p.id === proxyId);
        if (!proxy) {
            showMessage('未找到指定的代理配置', 'error');
            return;
        }
        
        // 填充表单
        fillProxyForm(proxy.config);
        showMessage(`已将 ${proxy.name} 填入表单`, 'info');
    } catch (error) {
        console.error('填充表单失败:', error);
        showMessage('填充表单失败: 网络错误', 'error');
    }
}

// 从历史记录删除代理配置
async function deleteProxyFromHistory(proxyId, phoneNumber) {
    if (!confirm('确定要删除这个代理配置吗？')) {
        return;
    }
    
    try {
        const response = await fetch('/account/delete_proxy_history', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                proxy_id: proxyId
            })
        });
        
        const data = await response.json();
        if (data.success) {
            showMessage('代理配置已删除', 'success');
            // 重新加载历史记录
            await loadProxyHistory(phoneNumber);
        } else {
            showMessage(`删除失败: ${data.message}`, 'error');
        }
    } catch (error) {
        console.error('删除代理失败:', error);
        showMessage('删除代理失败: 网络错误', 'error');
    }
}

// ==================== 历史记录查看功能 ====================

async function showFullHistoryModal(phoneNumber) {
    try {
        // 获取完整历史记录
        const response = await fetch(`/account/history?phone_number=${phoneNumber}&limit=100`);
        const data = await response.json();
        
        if (data.success) {
            const history = data.history || [];
            renderFullHistoryModal(phoneNumber, history);
        } else {
            showMessage(`获取历史记录失败: ${data.message}`, 'error');
        }
    } catch (error) {
        showMessage(`获取历史记录失败: ${error.message}`, 'error');
    }
}

function renderFullHistoryModal(phoneNumber, history) {
    // 创建模态框HTML
    const modalHtml = `
        <div id="fullHistoryModal" class="pre-publish-modal show">
            <div class="pre-publish-card" style="max-width: 900px;">
                <div class="pre-publish-header">
                    <h3>📋 ${phoneNumber} 完整历史记录</h3>
                    <button type="button" class="pre-publish-close" onclick="closeFullHistoryModal()">×</button>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                        <button class="btn-small" onclick="filterHistory('all')" id="filter-all">全部 (${history.length})</button>
                        <button class="btn-small" onclick="filterHistory('publish')" id="filter-publish">发布记录 (${history.filter(h => (h.action_type || h.type) === 'publish').length})</button>
                        <button class="btn-small" onclick="filterHistory('comment')" id="filter-comment">评论记录 (${history.filter(h => (h.action_type || h.type) === 'comment').length})</button>
                        <button class="btn-small" onclick="filterHistory('like')" id="filter-like">点赞记录 (${history.filter(h => (h.action_type || h.type) === 'like').length})</button>
                        <button class="btn-small" onclick="filterHistory('collect')" id="filter-collect">收藏记录 (${history.filter(h => (h.action_type || h.type) === 'collect').length})</button>
                    </div>
                </div>
                
                <div id="historyContainer" style="max-height: 60vh; overflow-y: auto;">
                    ${history.length > 0 ? renderHistoryItems(history) : '<div class="pre-publish-empty"><div class="pre-publish-empty-icon">📭</div><div>暂无历史记录</div></div>'}
                </div>
            </div>
        </div>
    `;
    
    // 移除已存在的模态框
    const existingModal = document.getElementById('fullHistoryModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // 添加模态框到页面
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // 设置默认筛选状态
    document.getElementById('filter-all').style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';
    
    // 存储当前历史数据供筛选使用
    window.currentFullHistory = history;
    window.currentHistoryPhone = phoneNumber;
}

function renderHistoryItems(history) {
    return history.map(item => {
        const isSuccess = item.success;
        const statusIcon = isSuccess ? '✅' : '❌';
        const statusClass = isSuccess ? 'success' : 'error';
        const actionType = item.action_type || item.type;
        
        if (actionType === 'publish') {
            return `
                <div class="history-item-full" data-type="${actionType}">
                    <div class="history-item-header">
                        <div class="history-item-type">📝 发布记录</div>
                        <div class="history-item-status ${statusClass}">${statusIcon}</div>
                    </div>
                    <div class="history-item-title">《${item.title}》</div>
                    <div class="history-item-content">${item.content}</div>
                    <div class="history-item-meta">
                        <span>📷 ${item.pic_count} 张图片</span>
                        <span>🕒 ${item.timestamp}</span>
                    </div>
                    ${item.result ? `<div class="history-item-result">结果: ${item.result}</div>` : ''}
                </div>
            `;
        } else if (actionType === 'comment') {
            return `
                <div class="history-item-full" data-type="${actionType}">
                    <div class="history-item-header">
                        <div class="history-item-type">💬 评论记录</div>
                        <div class="history-item-status ${statusClass}">${statusIcon}</div>
                    </div>
                    <div class="history-item-content">${item.comment}</div>
                    <div class="history-item-meta">
                        <span>🔗 ${item.url || '未知链接'}</span>
                        <span>🕒 ${item.timestamp}</span>
                    </div>
                    ${item.result ? `<div class="history-item-result">结果: ${item.result}</div>` : ''}
                </div>
            `;
        } else if (actionType === 'like') {
            return `
                <div class="history-item-full" data-type="${actionType}">
                    <div class="history-item-header">
                        <div class="history-item-type">👍 点赞记录</div>
                        <div class="history-item-status ${statusClass}">${statusIcon}</div>
                    </div>
                    <div class="history-item-content">为笔记点赞</div>
                    <div class="history-item-meta">
                        <span>🔗 ${item.url || '未知链接'}</span>
                        <span>🕒 ${item.timestamp}</span>
                    </div>
                    ${item.result ? `<div class="history-item-result">结果: ${item.result}</div>` : ''}
                </div>
            `;
        } else if (actionType === 'collect') {
            return `
                <div class="history-item-full" data-type="${actionType}">
                    <div class="history-item-header">
                        <div class="history-item-type">⭐ 收藏记录</div>
                        <div class="history-item-status ${statusClass}">${statusIcon}</div>
                    </div>
                    <div class="history-item-content">收藏笔记</div>
                    <div class="history-item-meta">
                        <span>🔗 ${item.url || '未知链接'}</span>
                        <span>🕒 ${item.timestamp}</span>
                    </div>
                    ${item.result ? `<div class="history-item-result">结果: ${item.result}</div>` : ''}
                </div>
            `;
        } else {
            // 兼容其他未知类型
            return `
                <div class="history-item-full" data-type="${actionType}">
                    <div class="history-item-header">
                        <div class="history-item-type">📋 ${actionType || '未知'} 记录</div>
                        <div class="history-item-status ${statusClass}">${statusIcon}</div>
                    </div>
                    <div class="history-item-content">${item.comment || item.content || '无内容'}</div>
                    <div class="history-item-meta">
                        <span>🔗 ${item.url || '未知链接'}</span>
                        <span>🕒 ${item.timestamp}</span>
                    </div>
                    ${item.result ? `<div class="history-item-result">结果: ${item.result}</div>` : ''}
                </div>
            `;
        }
    }).join('');
}

function filterHistory(type) {
    const history = window.currentFullHistory || [];
    const phoneNumber = window.currentHistoryPhone || '';
    
    // 重置按钮样式
    document.getElementById('filter-all').style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    document.getElementById('filter-publish').style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    document.getElementById('filter-comment').style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    document.getElementById('filter-like').style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    document.getElementById('filter-collect').style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    
    // 设置活跃按钮样式
    document.getElementById(`filter-${type}`).style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';
    
    // 筛选历史记录
    let filteredHistory = history;
    if (type === 'publish') {
        filteredHistory = history.filter(h => (h.action_type || h.type) === 'publish');
    } else if (type === 'comment') {
        filteredHistory = history.filter(h => (h.action_type || h.type) === 'comment');
    } else if (type === 'like') {
        filteredHistory = history.filter(h => (h.action_type || h.type) === 'like');
    } else if (type === 'collect') {
        filteredHistory = history.filter(h => (h.action_type || h.type) === 'collect');
    }
    
    // 更新显示
    const container = document.getElementById('historyContainer');
    container.innerHTML = filteredHistory.length > 0 ? 
        renderHistoryItems(filteredHistory) : 
        '<div class="pre-publish-empty"><div class="pre-publish-empty-icon">📭</div><div>暂无此类型的历史记录</div></div>';
}

function closeFullHistoryModal() {
    const modal = document.getElementById('fullHistoryModal');
    if (modal) {
        modal.classList.remove('show');
        setTimeout(() => {
            modal.remove();
        }, 300);
    }
    
    // 清理全局变量
    window.currentFullHistory = null;
    window.currentHistoryPhone = null;
}

// ==================== 移动端相关功能 ====================

// 移动端滑动状态
let mobileSwipeState = {
    currentIndex: 0,
    totalAccounts: 0,
    startX: 0,
    startY: 0,
    currentX: 0,
    currentY: 0,
    isDragging: false,
    threshold: 50
};

// 检测是否为移动设备
function isMobileDevice() {
    return window.innerWidth <= 768 || /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

// 初始化移动端滑动功能
function initMobileSwipe() {
    if (!isMobileDevice()) return;
    
    const wrapper = document.getElementById('mobileAccountsWrapper');
    if (!wrapper) return;
    
    // 移除之前绑定的事件监听器
    wrapper.removeEventListener('touchstart', handleTouchStart);
    wrapper.removeEventListener('touchmove', handleTouchMove);
    wrapper.removeEventListener('touchend', handleTouchEnd);
    wrapper.removeEventListener('mousedown', handleMouseDown);
    wrapper.removeEventListener('mousemove', handleMouseMove);
    wrapper.removeEventListener('mouseup', handleMouseUp);
    wrapper.removeEventListener('mouseleave', handleMouseUp);
    
    // 添加触摸事件
    wrapper.addEventListener('touchstart', handleTouchStart, { passive: false });
    wrapper.addEventListener('touchmove', handleTouchMove, { passive: false });
    wrapper.addEventListener('touchend', handleTouchEnd, { passive: false });
    
    // 添加鼠标事件（用于桌面端测试）
    wrapper.addEventListener('mousedown', handleMouseDown);
    wrapper.addEventListener('mousemove', handleMouseMove);
    wrapper.addEventListener('mouseup', handleMouseUp);
    wrapper.addEventListener('mouseleave', handleMouseUp);
    
    // 为特殊区域添加特殊处理（历史记录、按钮等）
    const specialElements = wrapper.querySelectorAll('.mobile-account-history, .btn, .mobile-account-actions, [onclick]');
    specialElements.forEach(element => {
        element.addEventListener('touchstart', function(e) {
            e.stopPropagation(); // 阻止事件冒泡到父容器
        }, { passive: true });
        
        element.addEventListener('touchmove', function(e) {
            e.stopPropagation(); // 阻止事件冒泡到父容器
        }, { passive: true });
    });
}

// 触摸开始
function handleTouchStart(e) {
    const touch = e.touches[0];
    handleDragStart(touch.clientX, touch.clientY);
}

// 鼠标按下
function handleMouseDown(e) {
    e.preventDefault();
    handleDragStart(e.clientX, e.clientY);
}

// 拖拽开始
function handleDragStart(x, y) {
    // 检查触摸点是否在特殊区域内（历史记录、按钮、预发布想法等）
    const target = document.elementFromPoint(x, y);
    if (target && (
        target.closest('.mobile-account-history') || 
        target.closest('.mobile-history-item') ||
        target.closest('.btn') ||
        target.closest('.mobile-account-actions') ||
        target.onclick || // 有点击事件的元素
        target.style.cursor === 'pointer' // 鼠标指针样式的元素
    )) {
        return; // 在特殊区域内，不启动拖拽
    }
    
    mobileSwipeState.startX = x;
    mobileSwipeState.startY = y;
    mobileSwipeState.currentX = x;
    mobileSwipeState.currentY = y;
    mobileSwipeState.isDragging = true;
    
    const wrapper = document.getElementById('mobileAccountsWrapper');
    if (wrapper) {
        wrapper.style.transition = 'none';
    }
}

// 触摸移动
function handleTouchMove(e) {
    if (!mobileSwipeState.isDragging) return;
    e.preventDefault();
    
    const touch = e.touches[0];
    handleDragMove(touch.clientX, touch.clientY);
}

// 鼠标移动
function handleMouseMove(e) {
    if (!mobileSwipeState.isDragging) return;
    e.preventDefault();
    handleDragMove(e.clientX, e.clientY);
}

// 拖拽移动
function handleDragMove(x, y) {
    mobileSwipeState.currentX = x;
    mobileSwipeState.currentY = y;
    
    const deltaX = mobileSwipeState.currentX - mobileSwipeState.startX;
    const deltaY = Math.abs(mobileSwipeState.currentY - mobileSwipeState.startY);
    
    // 如果垂直滑动距离大于水平滑动距离，则不处理（让页面正常滚动）
    if (deltaY > Math.abs(deltaX)) {
        return;
    }
    
    // 检查是否在特殊区域内
    const target = document.elementFromPoint(mobileSwipeState.startX, mobileSwipeState.startY);
    if (target && (
        target.closest('.mobile-account-history') || 
        target.closest('.mobile-history-item') ||
        target.closest('.btn') ||
        target.closest('.mobile-account-actions') ||
        target.onclick ||
        target.style.cursor === 'pointer'
    )) {
        return; // 在特殊区域内，不处理水平滑动
    }
    
    const wrapper = document.getElementById('mobileAccountsWrapper');
    if (wrapper) {
        const currentTransform = -mobileSwipeState.currentIndex * 100;
        const dragPercent = (deltaX / window.innerWidth) * 100;
        const newTransform = currentTransform + dragPercent;
        
        wrapper.style.transform = `translateX(${newTransform}%)`;
    }
}

// 触摸结束
function handleTouchEnd(e) {
    handleDragEnd();
}

// 鼠标释放
function handleMouseUp(e) {
    handleDragEnd();
}

// 拖拽结束
function handleDragEnd() {
    if (!mobileSwipeState.isDragging) return;
    
    const deltaX = mobileSwipeState.currentX - mobileSwipeState.startX;
    const threshold = mobileSwipeState.threshold;
    
    mobileSwipeState.isDragging = false;
    
    if (Math.abs(deltaX) > threshold) {
        if (deltaX > 0 && mobileSwipeState.currentIndex > 0) {
            // 向右滑动，显示上一个
            mobileSwipeState.currentIndex--;
        } else if (deltaX < 0 && mobileSwipeState.currentIndex < mobileSwipeState.totalAccounts - 1) {
            // 向左滑动，显示下一个
            mobileSwipeState.currentIndex++;
        }
    }
    
    updateMobileSwipePosition();
    updateSwipeIndicators();
}

// 更新移动端滑动位置
function updateMobileSwipePosition() {
    const wrapper = document.getElementById('mobileAccountsWrapper');
    if (wrapper) {
        wrapper.style.transition = 'transform 0.3s ease';
        wrapper.style.transform = `translateX(-${mobileSwipeState.currentIndex * 100}%)`;
    }
}

// 更新滑动指示器
function updateSwipeIndicators() {
    const indicators = document.querySelectorAll('.swipe-dot');
    indicators.forEach((dot, index) => {
        if (index === mobileSwipeState.currentIndex) {
            dot.classList.add('active');
        } else {
            dot.classList.remove('active');
        }
    });
}

// 跳转到指定卡片
function swipeToAccount(index) {
    if (index >= 0 && index < mobileSwipeState.totalAccounts) {
        mobileSwipeState.currentIndex = index;
        updateMobileSwipePosition();
        updateSwipeIndicators();
    }
}

// 渲染移动端账号卡片
function renderMobileAccounts(statusData, historyData, currentAccount, prePublishData = {}) {
    if (!isMobileDevice()) return;
    
    const wrapper = document.getElementById('mobileAccountsWrapper');
    const indicators = document.getElementById('swipeIndicators');
    const accountCount = document.getElementById('accountCount');
    
    if (!wrapper || !indicators) return;
    
    const accounts = Object.entries(statusData);
    mobileSwipeState.totalAccounts = accounts.length;
    mobileSwipeState.currentIndex = Math.min(mobileSwipeState.currentIndex, accounts.length - 1);
    
    if (accountCount) {
        accountCount.textContent = accounts.length;
    }
    
    if (accounts.length === 0) {
        wrapper.innerHTML = '<div class="mobile-account-slide"><div class="mobile-account-card"><div class="loading">暂无账号，请先添加账号</div></div></div>';
        indicators.innerHTML = '';
        return;
    }
    
    // 渲染移动端账号卡片
    let html = '';
    let indicatorsHtml = '';
    
    accounts.forEach(([phoneNumber, status], index) => {
        const history = historyData[phoneNumber] || [];
        const recentHistory = history.slice(-3).reverse();
        const isDefault = phoneNumber === currentAccount;
        const prePublishes = prePublishData[phoneNumber] || [];
        
        html += `
            <div class="mobile-account-slide">
                <div class="mobile-account-card">
                    <div class="mobile-account-header">
                        <div class="mobile-account-phone">
                            ${phoneNumber}
                            ${isDefault ? '<br><span style="color: #667eea; font-size: 0.8em;">【默认账号】</span>' : ''}
                        </div>
                        <div class="mobile-status-badge status-${status.status}">${getStatusText(status.status)}</div>
                        ${prePublishes.length > 0 ? `
                            <div onclick="togglePrePublishList('${phoneNumber}')" style="position: absolute; top: 15px; right: 15px; background: #ffa500; color: white; border-radius: 50%; width: 35px; height: 35px; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 12px rgba(255, 165, 0, 0.3); transition: all 0.3s ease;" onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'" ontouchstart="this.style.transform='scale(1.1)'" ontouchend="this.style.transform='scale(1)'">
                                💡${prePublishes.length}
                            </div>
                        ` : ''}
                    </div>
                    
                    <div class="mobile-account-stats">
                        <div class="mobile-stat-item">
                            <span class="mobile-stat-number">${status.publish_count || 0}</span>
                            <div class="mobile-stat-label">发布数</div>
                        </div>
                        <div class="mobile-stat-item">
                            <span class="mobile-stat-number">${status.comment_count || 0}</span>
                            <div class="mobile-stat-label">评论数</div>
                        </div>
                        <div class="mobile-stat-item">
                            <span class="mobile-stat-number">${status.like_count !== undefined ? status.like_count : 0}</span>
                            <div class="mobile-stat-label">点赞数</div>
                        </div>
                        <div class="mobile-stat-item">
                            <span class="mobile-stat-number">${status.collect_count !== undefined ? status.collect_count : 0}</span>
                            <div class="mobile-stat-label">收藏数</div>
                        </div>
                    </div>
                    
                    <div style="margin: 20px 0; font-size: 0.9em; color: #666; background: #f8f9fa; padding: 15px; border-radius: 10px;">
                        <div style="margin-bottom: 8px;">🌐 浏览器: <strong>${getBrowserStatusText(status.browser_status)}</strong></div>
                        <div style="margin-bottom: 8px;">🔄 刷新: <strong>${getRefreshStatusText(status.refresh_status)}</strong></div>
                        <div style="margin-bottom: 8px;">⏰ 心跳: ${formatTime(status.last_heartbeat)}</div>
                        <div>🍪 Cookie: ${status.cookie_exists ? '✅ 存在' : '❌ 不存在'}</div>
                    </div>
                    
                    ${prePublishes.length > 0 ? `
                        <div style="margin: 15px 0; background: linear-gradient(135deg, #ffa500 0%, #ff8c00 100%); border-radius: 12px; padding: 15px; color: white; cursor: pointer; box-shadow: 0 4px 15px rgba(255, 165, 0, 0.3); transition: all 0.3s ease;" onclick="togglePrePublishList('${phoneNumber}')" ontouchstart="this.style.transform='scale(0.98)'" ontouchend="this.style.transform='scale(1)'">
                            <div style="display: flex; align-items: center; justify-content: space-between;">
                                <div style="display: flex; align-items: center; gap: 10px;">
                                    <div style="font-size: 1.5em;">💡</div>
                                    <div>
                                        <div style="font-weight: 600; font-size: 1em;">预发布想法</div>
                                        <div style="font-size: 0.9em; opacity: 0.9;">${prePublishes.length} 个新想法等待发布</div>
                                    </div>
                                </div>
                                <div style="font-size: 1.2em;">👉</div>
                            </div>
                        </div>
                    ` : ''}
                    
                    <div class="mobile-account-actions">
                        <button class="btn btn-emoji" onclick="updateHeartbeat('${phoneNumber}')" title="更新心跳">
                            💓
                            <div class="btn-emoji-text">心跳</div>
                        </button>
                        ${!isDefault ? 
                            `<button class="btn btn-emoji" onclick="setDefaultAccount('${phoneNumber}')" title="设为默认账号">
                                ⭐
                                <div class="btn-emoji-text">默认</div>
                            </button>` : 
                            `<button class="btn btn-emoji" disabled style="opacity: 0.5;" title="当前默认账号">
                                ✅
                                <div class="btn-emoji-text">默认</div>
                            </button>`
                        }
                        <button class="btn btn-emoji" onclick="showAddPrePublishModal('${phoneNumber}')" title="${prePublishes.length > 0 ? `管理预发布(${prePublishes.length})` : '添加预发布'}">
                            💡
                            <div class="btn-emoji-text">${prePublishes.length > 0 ? `想法(${prePublishes.length})` : '想法'}</div>
                        </button>
                        <button class="btn btn-emoji" onclick="showAccountSettingsModal('${phoneNumber}')" title="账号设置">
                            ⚙️
                            <div class="btn-emoji-text">设置</div>
                        </button>
                        ${status.refresh_status === 'running' ? 
                            `<button class="btn btn-emoji" onclick="stopAutoRefresh('${phoneNumber}')" title="停止自动刷新">
                                ⏹️
                                <div class="btn-emoji-text">停止</div>
                            </button>` : 
                            `<button class="btn btn-emoji" onclick="startAutoRefresh('${phoneNumber}')" title="启动自动刷新">
                                ▶️
                                <div class="btn-emoji-text">启动</div>
                            </button>`
                        }
                        <button class="btn btn-emoji" onclick="showFullHistoryModal('${phoneNumber}')" title="查看完整历史">
                            📋
                            <div class="btn-emoji-text">历史</div>
                        </button>
                        <button class="btn btn-emoji" onclick="removeAccount('${phoneNumber}')" title="删除账号" style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); color: white;">
                            🗑️
                            <div class="btn-emoji-text">删除</div>
                        </button>
                    </div>
                    
                    ${history.length > 0 ? `
                        <div class="mobile-account-history">
                            ${history.length > 5 ? '<div class="mobile-history-scroll-hint">可滚动</div>' : ''}
                            <h4 style="margin-bottom: 10px; color: #333; font-size: 1em;">📋 历史活动 (${history.length}条)</h4>
                            ${history.slice(-10).reverse().map(item => `
                                <div class="mobile-history-item">
                                    <div class="mobile-history-time">${formatDateTime(item.timestamp)}</div>
                                    <div class="mobile-history-content">${getMobileHistoryDisplayText(item)}</div>
                                </div>
                            `).join('')}
                            <div style="text-align: center; margin-top: 10px;">
                                <button class="btn btn-small" onclick="showFullHistoryModal('${phoneNumber}')">
                                    ${history.length > 10 ? `查看全部 ${history.length} 条记录` : '查看完整历史'}
                                </button>
                            </div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
        
        indicatorsHtml += `<div class="swipe-dot ${index === mobileSwipeState.currentIndex ? 'active' : ''}" onclick="swipeToAccount(${index})"></div>`;
    });
    
    wrapper.innerHTML = html;
    indicators.innerHTML = indicatorsHtml;
    
    // 设置初始位置
    updateMobileSwipePosition();
    
    // 初始化滑动功能
    setTimeout(() => {
        initMobileSwipe();
    }, 100);
}

// 渲染移动端Cookies历史记录
function renderMobileCookiesHistory(cookiesFiles) {
    if (!isMobileDevice()) return;
    
    const container = document.getElementById('mobileCookiesHistoryContainer');
    if (!container) return;
    
    if (cookiesFiles.length === 0) {
        container.innerHTML = '<div class="loading">未发现历史登录账号</div>';
        container.style.display = 'block';
        return;
    }
    
    let html = '';
    cookiesFiles.forEach(file => {
        const phoneNumber = file.phone_number || '未知号码';
        const isActive = file.is_active; // 修复：使用正确的属性名
        
        html += `
            <div class="mobile-cookie-card">
                <div class="mobile-cookie-header">
                    <div class="mobile-cookie-phone">${phoneNumber}</div>
                    <div class="cookie-status-badge ${isActive ? 'cookie-status-active' : 'cookie-status-inactive'}">
                        ${isActive ? '当前' : '历史'}
                    </div>
                </div>
                <div class="mobile-cookie-info">
                    <div>📁 文件: ${file.filename}</div>
                    <div>📅 修改时间: ${file.last_modified_date}</div>
                    <div>💾 文件大小: ${file.file_size_kb} KB</div>
                    <div>🍪 Cookies数: ${file.cookies_count}</div>
                </div>
                ${!isActive ? `
                    <div class="mobile-cookie-actions">
                        <button class="btn btn-success" onclick="addAccountFromCookies('${phoneNumber}')">快速添加</button>
                    </div>
                ` : `
                    <div class="cookie-history-active-status">✅ 当前使用的账号</div>
                `}
            </div>
        `;
    });
    
    container.innerHTML = html;
    container.style.display = 'grid';
}



// 切换Cookies历史记录区域的显示/隐藏
function toggleCookiesHistorySection() {
    const section = document.getElementById('cookiesHistorySection');
    const icon = document.getElementById('cookiesToggleIcon');
    const text = document.getElementById('cookiesToggleText');
    
    if (section && icon && text) {
        section.classList.toggle('collapsed');
        
        if (section.classList.contains('collapsed')) {
            icon.textContent = '👁️';
            text.textContent = '显示';
        } else {
            icon.textContent = '🙈';
            text.textContent = '隐藏';
        }
    }
}

// 监听窗口大小变化
window.addEventListener('resize', function() {
    // 延迟执行以避免频繁触发
    clearTimeout(window.resizeTimer);
    window.resizeTimer = setTimeout(() => {
        if (isMobileDevice()) {
            // 重新初始化移动端功能
            initMobileSwipe();
            updateMobileSwipePosition();
        }
    }, 250);
});