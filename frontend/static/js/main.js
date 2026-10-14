/* ================================================
   SI PENGADUAN - Main JavaScript
   ================================================ */

document.addEventListener('DOMContentLoaded', function () {

    // ── Sidebar Toggle ────────────────────────────
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    const sidebarToggle = document.getElementById('sidebarToggle');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            if (window.innerWidth <= 768) {
                // Mobile: show overlay
                sidebar.classList.toggle('mobile-open');
                let overlay = document.querySelector('.sidebar-overlay');
                if (!overlay) {
                    overlay = document.createElement('div');
                    overlay.className = 'sidebar-overlay';
                    document.body.appendChild(overlay);
                }
                overlay.style.display = sidebar.classList.contains('mobile-open') ? 'block' : 'none';
                overlay.addEventListener('click', () => {
                    sidebar.classList.remove('mobile-open');
                    overlay.style.display = 'none';
                });
            } else {
                // Desktop: collapse sidebar
                sidebar.classList.toggle('collapsed');
                mainContent.classList.toggle('expanded');
                localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
            }
        });

        // Restore sidebar state
        const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        if (isCollapsed && window.innerWidth > 768) {
            sidebar.classList.add('collapsed');
            mainContent.classList.add('expanded');
        }
    }

    // ── Auto-dismiss Flash Toasts ─────────────────
    const toasts = document.querySelectorAll('.alert-toast');
    toasts.forEach((toast, index) => {
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 4000 + (index * 500));
    });

    // ── Category Card Selection ───────────────────
    const categoryCards = document.querySelectorAll('.category-card-option');
    categoryCards.forEach(card => {
        card.addEventListener('click', () => {
            categoryCards.forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            const input = card.querySelector('input[type="radio"]');
            if (input) input.checked = true;
        });
    });

    // ── File Upload Area ──────────────────────────
    const uploadArea = document.querySelector('.upload-area');
    const fileInput = document.querySelector('#attachmentInput');
    const filePreviewList = document.querySelector('#filePreviewList');

    if (uploadArea && fileInput) {
        uploadArea.addEventListener('click', () => fileInput.click());

        uploadArea.addEventListener('dragover', e => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', e => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const dt = new DataTransfer();
            const existingFiles = fileInput.files;
            for (let f of existingFiles) dt.items.add(f);
            for (let f of e.dataTransfer.files) dt.items.add(f);
            fileInput.files = dt.files;
            updateFilePreview();
        });

        fileInput.addEventListener('change', updateFilePreview);
    }

    function updateFilePreview() {
        if (!filePreviewList || !fileInput) return;
        filePreviewList.innerHTML = '';

        Array.from(fileInput.files).forEach((file, idx) => {
            const size = formatFileSize(file.size);
            const ext = file.name.split('.').pop().toUpperCase();
            const isImage = ['PNG','JPG','JPEG','GIF','WEBP'].includes(ext);

            const item = document.createElement('div');
            item.className = 'file-preview-item';
            item.innerHTML = `
                <div class="file-icon ${isImage ? 'file-icon-image' : 'file-icon-doc'}">
                    <i class="bi ${isImage ? 'bi-image-fill' : 'bi-file-earmark-fill'}"></i>
                </div>
                <div class="file-info">
                    <span class="file-name">${file.name}</span>
                    <span class="file-size">${ext} · ${size}</span>
                </div>
                <button type="button" class="file-remove-btn" onclick="removeFile(${idx})">
                    <i class="bi bi-x"></i>
                </button>
            `;

            if (isImage) {
                const reader = new FileReader();
                reader.onload = e => {
                    const thumb = document.createElement('img');
                    thumb.src = e.target.result;
                    thumb.className = 'file-thumb';
                    item.prepend(thumb);
                    item.querySelector('.file-icon').style.display = 'none';
                };
                reader.readAsDataURL(file);
            }

            filePreviewList.appendChild(item);
        });
    }

    window.removeFile = function(idx) {
        if (!fileInput) return;
        const dt = new DataTransfer();
        Array.from(fileInput.files).forEach((f, i) => {
            if (i !== idx) dt.items.add(f);
        });
        fileInput.files = dt.files;
        updateFilePreview();
    };

    // ── Confirmation Modal ────────────────────────
    const complaintForm = document.getElementById('complaintForm');
    const confirmModal = document.getElementById('confirmModal');
    const confirmSubmitBtn = document.getElementById('confirmSubmitBtn');
    const cancelConfirmBtn = document.getElementById('cancelConfirmBtn');

    if (complaintForm && confirmModal) {
        complaintForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const title = document.getElementById('title')?.value?.trim();
            const description = document.getElementById('description')?.value?.trim();
            const category = document.querySelector('input[name="category"]:checked')?.value;

            if (!title || !description || !category) {
                showToast('Harap lengkapi semua field yang wajib diisi.', 'danger');
                return;
            }

            if (description.length < 20) {
                showToast('Deskripsi minimal 20 karakter.', 'danger');
                return;
            }

            // Fill confirm modal preview
            if (document.getElementById('previewTitle')) {
                document.getElementById('previewTitle').textContent = title;
            }
            if (document.getElementById('previewCategory')) {
                document.getElementById('previewCategory').textContent = category;
            }

            confirmModal.classList.add('show');
        });

        if (cancelConfirmBtn) {
            cancelConfirmBtn.addEventListener('click', () => {
                confirmModal.classList.remove('show');
            });
        }

        confirmModal.addEventListener('click', e => {
            if (e.target === confirmModal) confirmModal.classList.remove('show');
        });

        if (confirmSubmitBtn) {
            confirmSubmitBtn.addEventListener('click', () => {
                confirmSubmitBtn.disabled = true;
                confirmSubmitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Mengirim...';
                complaintForm.submit();
            });
        }
    }

    // ── Sync Theme on load ────────────────────────
    const savedTheme = localStorage.getItem('user_theme') || 'dark';
    if (savedTheme === 'light') {
        document.documentElement.setAttribute('data-bs-theme', 'light');
        document.documentElement.setAttribute('data-theme', 'light');
        document.documentElement.classList.add('light-theme');
        if (document.body) {
            document.body.classList.add('light-theme');
            document.body.classList.remove('dark');
        }
    }

    // ── Real-Time Notification & Audio Alert System ─────────
    let lastNotifCount = null;

    function playUserNotificationAlert() {
        const soundEnabled = localStorage.getItem('user_notif_sound_enabled') !== 'false';
        if (!soundEnabled) return;

        const soundKey = localStorage.getItem('user_notif_sound') || 'chime';
        const soundUrls = {
            'chime': '/static/audio/chime.mp3',
            'bell': '/static/audio/bell.mp3',
            'pop': '/static/audio/pop.mp3',
            'gentle': '/static/audio/gentle.mp3'
        };
        const url = soundUrls[soundKey] || soundUrls['chime'];
        const vol = parseInt(localStorage.getItem('user_notif_volume') || '80', 10) / 100;

        try {
            const audio = new Audio(url + '?t=' + Date.now());
            audio.volume = vol;
            const promise = audio.play();
            if (promise !== undefined) {
                promise.catch(e => console.log('Autoplay prevented until user gesture:', e.message));
            }
        } catch (e) {}
    }

    function pollNotifications() {
        fetch('/notifications/count')
            .then(r => r.json())
            .then(data => {
                const badge = document.querySelector('.notif-dot');
                const sidebarBadge = document.querySelector('.notif-badge');
                const count = (data && typeof data.count === 'number') ? data.count : 0;

                if (count > 0) {
                    if (badge) { badge.textContent = count; badge.style.display = 'flex'; }
                    if (sidebarBadge) { sidebarBadge.textContent = count; sidebarBadge.style.display = 'inline'; }

                    // If notification count increased, play alert chime!
                    if (lastNotifCount !== null && count > lastNotifCount) {
                        playUserNotificationAlert();
                        showToast('Ada tanggapan atau pembaruan baru dari admin!', 'info');
                    }
                } else {
                    if (badge) badge.style.display = 'none';
                    if (sidebarBadge) sidebarBadge.style.display = 'none';
                }
                lastNotifCount = count;
            })
            .catch(() => {});
    }

    // Poll every 5 seconds for real-time updates & on focus
    if (document.getElementById('mainContent')) {
        pollNotifications();
        setInterval(pollNotifications, 5000);
        window.addEventListener('focus', pollNotifications);
    }

    // ── Character Counter ─────────────────────────
    const descTextarea = document.getElementById('description');
    const charCounter = document.getElementById('charCounter');

    if (descTextarea && charCounter) {
        descTextarea.addEventListener('input', () => {
            const len = descTextarea.value.length;
            charCounter.textContent = `${len} karakter ${len < 20 ? '(minimal 20)' : '✓'}`;
            charCounter.style.color = len < 20 ? '#f59e0b' : '#10b981';
        });
    }

    // ── Copy Ticket Number ────────────────────────
    const copyTicketBtn = document.querySelectorAll('.copy-ticket-btn');
    copyTicketBtn.forEach(btn => {
        btn.addEventListener('click', () => {
            const ticket = btn.dataset.ticket;
            navigator.clipboard.writeText(ticket).then(() => {
                const originalHTML = btn.innerHTML;
                btn.innerHTML = '<i class="bi bi-check2"></i>';
                btn.style.color = 'var(--accent-green)';
                setTimeout(() => {
                    btn.innerHTML = originalHTML;
                    btn.style.color = '';
                }, 2000);
            });
        });
    });

    // ── Toast Utility ─────────────────────────────
    function showToast(message, type = 'info') {
        const container = document.getElementById('flashContainer') || document.body;
        const icons = {
            success: 'bi-check-circle-fill',
            danger: 'bi-x-circle-fill',
            warning: 'bi-exclamation-triangle-fill',
            info: 'bi-info-circle-fill'
        };
        const toast = document.createElement('div');
        toast.className = `alert-toast alert-toast-${type}`;
        toast.innerHTML = `
            <div class="alert-toast-icon"><i class="bi ${icons[type] || icons.info}"></i></div>
            <div class="alert-toast-body">${message}</div>
            <button class="alert-toast-close" onclick="this.parentElement.remove()"><i class="bi bi-x"></i></button>
        `;
        container.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }

    // ── Avatar Preview ────────────────────────────
    const avatarInput = document.getElementById('avatarInput');
    const avatarPreview = document.getElementById('avatarPreview');

    if (avatarInput && avatarPreview) {
        avatarInput.addEventListener('change', function () {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = e => {
                    avatarPreview.src = e.target.result;
                    avatarPreview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // ── Filter Form Auto-Submit ───────────────────
    const filterSelects = document.querySelectorAll('.filter-auto-submit');
    filterSelects.forEach(select => {
        select.addEventListener('change', () => {
            select.closest('form')?.submit();
        });
    });

    // ── Smooth Animations on scroll ───────────────
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        observer.observe(el);
    });
});

// ── File size formatter ───────────────────────────
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
}
