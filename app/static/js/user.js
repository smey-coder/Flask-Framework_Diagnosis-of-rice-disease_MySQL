document.addEventListener("DOMContentLoaded", function () {
    // =========================================================
    // CSRF TOKEN
    // ========================================================
    const csrfToken =document.querySelector('meta[name="csrf-token"]')?.content || "";
    // =========================================================
    // NOTIFICATION URLS
    // =========================================================
    const notifUrl =
        "{{ url_for('user.get_notifications') }}";
    const deleteNotificationUrl =
        "{{ url_for('user.delete_notification', id=0) }}";
    const deleteAllUrl =
        "{{ url_for('user.delete_all_notifications') }}";
    const readNotificationUrl =
        "{{ url_for('user.read_notification', id=0) }}";
    const diseaseDetailUrl =
        "{{ url_for('user.disease_detail', id=0) }}";
    // const cropMonitoringDetailUrl =
    //     "{{ url_for('user.crop_notification_detail', monitoring_id=0) }}";
    const cropMonitoringDetailUrl =
    "{{ url_for('user.crop_monitoring_detail_page', monitoring_id=0) }}";
    // =========================================================
    // DEBUG
    // =========================================================

    console.log("=================================");
    console.log("Notification System Initialized");
    console.log("Notification URL:", notifUrl);
    console.log("Delete URL:", deleteNotificationUrl);
    console.log("Read URL:", readNotificationUrl);
    console.log("Crop Detail URL:", cropMonitoringDetailUrl);
    console.log("=================================");
    // =========================================================
    // TIME AGO
    // =========================================================
    function timeAgo(time) {
        if (!time) {
            return "";
        }
        const now = new Date();
        const past = new Date(time);
        const diff = Math.floor(
            (now - past) / 1000
        );
        if (diff < 60) {
            return "Just now";
        }
        if (diff < 3600) {

            return (
                Math.floor(diff / 60) +
                " min ago"
            );
        }

        if (diff < 86400) {

            return (
                Math.floor(diff / 3600) +
                " hrs ago"
            );
        }

        return (
            Math.floor(diff / 86400) +
            " days ago"
        );
    }


    // =========================================================
    // ESCAPE HTML
    // =========================================================

    function escapeHtml(value) {

        if (
            value === null ||
            value === undefined
        ) {
            return "";
        }

        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }


    // =========================================================
    // GET NOTIFICATION ICON
    // =========================================================

    function getNotificationIcon(notification) {

        // Backend icon has highest priority
        if (notification.icon) {
            return notification.icon;
        }


        // Disease
        if (
            notification.category ===
            "disease"
        ) {
            return "bi-virus";
        }


        // Crop Monitoring
        if (
            notification.category ===
            "crop_monitoring"
        ) {
            return "bi-flower1";
        }


        // Critical
        if (
            notification.type ===
            "critical"
        ) {
            return "bi-exclamation-triangle-fill";
        }


        // Warning
        if (
            notification.type ===
            "warning"
        ) {
            return "bi-exclamation-circle-fill";
        }


        // Default
        return "bi-info-circle";
    }


    // =========================================================
    // GET NOTIFICATION COLOR
    // =========================================================

    function getNotificationColor(notification) {

        if (
            notification.type ===
            "critical"
        ) {
            return "text-danger";
        }


        if (
            notification.type ===
            "warning"
        ) {
            return "text-warning";
        }


        if (
            notification.category ===
            "disease"
        ) {
            return "text-success";
        }


        if (
            notification.category ===
            "crop_monitoring"
        ) {
            return "text-primary";
        }


        return "text-secondary";
    }


    // =========================================================
    // GET CATEGORY LABEL
    // =========================================================

    function getCategoryLabel(notification) {

        if (
            notification.category ===
            "disease"
        ) {
            return "Disease";
        }


        if (
            notification.category ===
            "crop_monitoring"
        ) {
            return "Crop Monitoring";
        }


        return "Notification";
    }


    // =========================================================
    // LOAD NOTIFICATIONS
    // =========================================================

    function loadNotifications() {
        console.log(
            "Loading notifications..."
        );
        fetch(notifUrl, {
            method: "GET",
            headers: {
                "Accept": "application/json"
            }
        })

        .then(response => {

            console.log(
                "Notification response:",
                response.status
            );


            if (!response.ok) {

                throw new Error(
                    "HTTP Error " +
                    response.status
                );
            }


            return response.json();
        })

        .then(data => {

            console.log(
                "Notification data:",
                data
            );


            // =================================================
            // GET ELEMENTS
            // =================================================

            const list =
                document.getElementById(
                    "notif-list"
                );

            const count =
                document.getElementById(
                    "notif-count"
                );


            if (!list) {

                console.error(
                    "Element #notif-list not found."
                );

                return;
            }


            if (!count) {

                console.error(
                    "Element #notif-count not found."
                );

                return;
            }


            // =================================================
            // CLEAR OLD LIST
            // =================================================

            list.innerHTML = "";


            // =================================================
            // SAFETY
            // =================================================

            if (!Array.isArray(data)) {

                console.error(
                    "Notification response is not an array:",
                    data
                );

                return;
            }


            // =================================================
            // UNREAD COUNT
            // =================================================

            const unreadCount =
                data.filter(
                    notification =>
                        !notification.is_read
                ).length;


            count.innerText =
                unreadCount > 0
                    ? unreadCount
                    : "";


            // =================================================
            // EMPTY
            // =================================================

            if (data.length === 0) {

                list.innerHTML = `

                    <div
                        class="text-center p-4"
                    >

                        <i
                            class="
                                bi
                                bi-bell-slash
                                fs-3
                                text-muted
                            "
                        ></i>

                        <div
                            class="
                                text-muted
                                mt-2
                            "
                        >
                            No notifications
                        </div>

                    </div>

                `;

                return;
            }


            // =================================================
            // RENDER EACH NOTIFICATION
            // =================================================

            data.forEach(notification => {

                const icon =
                    getNotificationIcon(
                        notification
                    );
                const color =
                    getNotificationColor(
                        notification
                    );

                const categoryLabel =
                    getCategoryLabel(
                        notification
                    );
                const title =
                    notification.title ||
                    notification.name ||
                    "Notification";


                const message =
                    notification.message ||
                    "";


                const safeTitle =
                    escapeHtml(title);


                const safeMessage =
                    escapeHtml(message);


                // =================================================
                // READ / UNREAD CLASS
                // =================================================

                const unreadClass =
                    notification.is_read
                        ? ""
                        : "notification-unread";


                // =================================================
                // CREATE ITEM
                // =================================================

                const item =
                    document.createElement(
                        "div"
                    );


                item.className = `
                    dropdown-item
                    notif-item
                    ${unreadClass}
                `;


                // =================================================
                // ITEM HTML
                // =================================================

                item.innerHTML = `

                    <div
                        class="
                            d-flex
                            align-items-start
                            gap-2
                        "
                    >

                        <!-- ICON -->

                        <div
                            class="
                                notification-icon
                                ${color}
                            "
                        >

                            <i
                                class="
                                    bi
                                    ${icon}
                                "
                            ></i>

                        </div>


                        <!-- CONTENT -->

                        <div
                            class="
                                flex-grow-1
                                notification-content
                            "
                            style="cursor:pointer;"
                        >

                            <div
                                class="
                                    small
                                    text-muted
                                    mb-1
                                "
                            >

                                ${categoryLabel}

                            </div>


                            <strong>
                                ${safeTitle}
                            </strong>


                            ${
                                safeMessage
                                    ? `
                                    <div
                                        class="
                                            small
                                            text-muted
                                            mt-1
                                        "
                                    >
                                        ${safeMessage}
                                    </div>
                                    `
                                    : ""
                            }


                            <small
                                class="
                                    text-muted
                                    d-block
                                    mt-1
                                "
                            >
                                ${timeAgo(
                                    notification.time
                                )}
                            </small>

                        </div>


                        <!-- DELETE -->

                        <button
                            type="button"
                            class="
                                btn
                                btn-sm
                                text-danger
                                notification-delete
                            "
                            title="Delete notification"
                        >

                            <i
                                class="
                                    bi
                                    bi-x-lg
                                "
                            ></i>

                        </button>

                    </div>

                `;


                // =================================================
                // OPEN EVENT
                // =================================================

                const content =
                    item.querySelector(
                        ".notification-content"
                    );

                if (content) {
                    content.addEventListener(
                        "click",
                        function () {
                            openNotification(
                                notification
                            );

                        }
                    );
                }


                // =================================================
                // DELETE EVENT
                // =================================================

                const deleteButton =
                    item.querySelector(
                        ".notification-delete"
                    );


                if (deleteButton) {

                    deleteButton.addEventListener(
                        "click",
                        function (event) {

                            event.preventDefault();

                            event.stopPropagation();

                            deleteNotification(
                                notification
                            );

                        }
                    );
                }


                // =================================================
                // ADD TO LIST
                // =================================================

                list.appendChild(item);

            });

        })

        .catch(error => {

            console.error(
                "❌ Load notifications error:",
                error
            );

        });
    }


    // =========================================================
    // OPEN NOTIFICATION
    // =========================================================

    window.openNotification =
    function (notification) {

        console.log(
            "Opening notification:",
            notification
        );


        // =====================================================
        // NOTIFICATION ID
        // =====================================================

        const notificationId =
            notification.notification_id ||
            notification.id;


        if (!notificationId) {

            console.error(
                "Notification ID missing:",
                notification
            );

            return;
        }


        // =====================================================
        // MARK AS READ URL
        // =====================================================

        const readUrl =
            readNotificationUrl.replace(
                "0",
                notificationId
            );


        // =====================================================
        // DISEASE
        // =====================================================

        if (
            notification.category ===
            "disease"
        ) {

            const diseaseId =
                notification.reference_id;


            if (!diseaseId) {

                console.error(
                    "Disease ID missing:",
                    notification
                );

                return;
            }


            const detailUrl =
                diseaseDetailUrl.replace(
                    "0",
                    diseaseId
                );


            markAsReadAndOpen(
                readUrl,
                detailUrl
            );


            return;
        }


        // =====================================================
        // CROP MONITORING
        // =====================================================

        if (
            notification.category ===
            "crop_monitoring"
        ) {

            const monitoringId =
                notification.reference_id;


            if (!monitoringId) {

                console.error(
                    "Monitoring ID missing:",
                    notification
                );

                return;
            }


            const detailUrl =
                cropMonitoringDetailUrl.replace(
                    "0",
                    monitoringId
                );


            markAsReadAndOpen(
                readUrl,
                detailUrl
            );


            return;
        }


        console.warn(
            "Unknown notification category:",
            notification.category
        );
    };


    // =========================================================
    // MARK AS READ THEN OPEN
    // =========================================================

    function markAsReadAndOpen(
        readUrl,
        detailUrl
    ) {

        console.log(
            "Mark notification as read:",
            readUrl
        );


        fetch(readUrl, {

            method: "POST",

            headers: {

                "X-CSRFToken":
                    csrfToken,

                "Accept":
                    "application/json"
            }

        })

        .then(response => {

            console.log(
                "Read response:",
                response.status
            );


            if (!response.ok) {

                throw new Error(
                    "Read failed: " +
                    response.status
                );
            }


            window.location.href =
                detailUrl;

        })

        .catch(error => {

            console.error(
                "Read notification error:",
                error
            );


            // Open detail even if read fails
            window.location.href =
                detailUrl;
        });
    }


    // =========================================================
    // DELETE ONE NOTIFICATION
    // =========================================================

    window.deleteNotification =
    function (notification) {

        console.log(
            "Deleting notification:",
            notification
        );


        // =====================================================
        // IMPORTANT:
        // Use UserNotification.id
        // =====================================================

        const notificationId =
            notification.notification_id ||
            notification.id;


        if (!notificationId) {

            console.error(
                "Notification ID missing:",
                notification
            );

            return;
        }


        const url =
            deleteNotificationUrl.replace(
                "0",
                notificationId
            );


        console.log(
            "Delete URL:",
            url
        );


        fetch(url, {

            method: "POST",

            headers: {

                "X-CSRFToken":
                    csrfToken,

                "Accept":
                    "application/json"
            }

        })

        .then(response => {

            console.log(
                "Delete response:",
                response.status
            );


            if (!response.ok) {

                throw new Error(
                    "Delete failed: " +
                    response.status
                );
            }


            // Reload list
            loadNotifications();

        })

        .catch(error => {

            console.error(
                "❌ Delete notification error:",
                error
            );

        });
    };


    // =========================================================
    // DELETE ALL
    // =========================================================

    window.deleteAll =
    function () {

        const confirmed =
            confirm(
                "Are you sure you want to delete all notifications?"
            );


        if (!confirmed) {
            return;
        }


        fetch(deleteAllUrl, {

            method: "POST",

            headers: {

                "X-CSRFToken":
                    csrfToken,

                "Accept":
                    "application/json"
            }

        })

        .then(response => {

            console.log(
                "Delete all response:",
                response.status
            );


            if (!response.ok) {

                throw new Error(
                    "Delete all failed: " +
                    response.status
                );
            }


            loadNotifications();

        })

        .catch(error => {

            console.error(
                "❌ Delete all error:",
                error
            );

        });
    };
    // =========================================================
    // INITIAL LOAD
    // =========================================================
    loadNotifications();
    // =========================================================
    // AUTO REFRESH
    // =========================================================
    setInterval(
        loadNotifications,
        5000
    );

});


document.addEventListener("DOMContentLoaded", function () {

    const toggle = document.getElementById("darkModeToggle");

    //Apply saved mode on ALL pages
    if (localStorage.getItem("darkMode") === "enabled") {
        document.body.classList.add("dark-mode");
    }

    // Only attach event if toggle exists (settings page)
    if (toggle) {

        // sync toggle state
        toggle.checked = localStorage.getItem("darkMode") === "enabled";

        toggle.addEventListener("change", function () {
            if (this.checked) {
                document.body.classList.add("dark-mode");
                localStorage.setItem("darkMode", "enabled");
            } else {
                document.body.classList.remove("dark-mode");
                localStorage.setItem("darkMode", "disabled");
            }
        });
    }

});

//Pup up button
document.addEventListener("DOMContentLoaded", function () {

    const backToTopBtn = document.getElementById("backToTopBtn");

    function toggleBackToTop() {
        if (window.scrollY > 300) {
            backToTopBtn.classList.add("show");
        } else {
            backToTopBtn.classList.remove("show");
        }
    }

    window.addEventListener("scroll", toggleBackToTop);

    backToTopBtn.addEventListener("click", function () {
        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    });

    toggleBackToTop();
});
