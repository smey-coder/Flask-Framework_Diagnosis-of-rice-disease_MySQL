function loadNotifications() {

    console.log("Loading notifications...");
    console.log("Notification URL:", notifUrl);

    fetch(notifUrl)
        .then(res => {

            console.log(
                "Notification response:",
                res.status
            );

            if (!res.ok) {
                throw new Error(
                    "HTTP error " + res.status
                );
            }

            return res.json();
        })
        .then(data => {

            console.log(
                "Notification data:",
                data
            );

            // existing code...
        })
        .catch(err => {

            console.error(
                "Notification error:",
                err
            );
        });
}
loadNotifications();