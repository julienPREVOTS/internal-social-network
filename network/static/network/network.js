document.addEventListener('DOMContentLoaded', function() {

    // Handle edit button click
    document.querySelectorAll('.edit-button').forEach(button => {
        button.onclick = () => {
            const postId = button.dataset.postId;
            const postContentElement = document.querySelector(`#post-${postId} .post-content`);
            const postContent = postContentElement.innerHTML.replace(/<br\s*\/?>/gi, "\n");

            document.querySelector(`#edit-content-${postId}`).value = postContent;
            document.querySelector(`#post-${postId} .post-content`).style.display = 'none';
            document.querySelector(`#post-${postId} .edit-button`).style.display = 'none';
            document.querySelector(`#post-${postId} .like-div`).style.display = 'none';
            document.querySelector(`#edit-form-${postId}`).style.display = 'block';
        };
    });

    // Handle cancel button click
    document.querySelectorAll('.cancel-button').forEach(button => {
        button.onclick = () => {
            const postId = button.dataset.postId;
            document.querySelector(`#post-${postId} .post-content`).style.display = 'block';
            document.querySelector(`#post-${postId} .edit-button`).style.display = 'block';
            document.querySelector(`#post-${postId} .like-div`).style.display = 'block';
            document.querySelector(`#edit-form-${postId}`).style.display = 'none';
        };
    });

    // Handle save button click
    document.querySelectorAll('.save-button').forEach(button => {
        button.onclick = () => {
            const postId = button.dataset.postId;
            const newContent = document.querySelector(`#edit-content-${postId}`).value;

            fetch(`/edit_post/${postId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    content: newContent
                })
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    document.querySelector(`#post-${postId} .post-content`).innerHTML = result.content.replace(/\n/g, '<br>'); 
                    document.querySelector(`#post-${postId} .post-content`).style.display = 'block';
                    document.querySelector(`#edit-form-${postId}`).style.display = 'none';
                    document.querySelector(`#post-${postId} .like-div`).style.display = 'block';
                    document.querySelector(`#post-${postId} .edit-button`).style.display = 'block';
                    // Format the date to match the template
                    const localDate = new Date(result.timestamp);

                    const months = [
                        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
                    ];

                    const day = localDate.getDate().toString().padStart(2, '0');
                    const month = months[localDate.getMonth()]; // Months are zero-based
                    const year = localDate.getFullYear();
                    const hours = localDate.getHours().toString().padStart(2, '0');
                    const minutes = localDate.getMinutes().toString().padStart(2, '0');
                    const seconds = localDate.getSeconds().toString().padStart(2, '0');

                    const formattedDate = `${day} ${month} ${year} ${hours}:${minutes}:${seconds}`;
                    document.querySelector(`#post-${postId} .post-timestamp`).innerHTML = formattedDate;
                } else {
                    console.error(result.error);
                }
            });
        };
    });

    document.querySelectorAll('.like-button').forEach(button => {
        button.onclick = function() {
            const postId = this.dataset.postId;
            fetch(`/like_post/${postId}`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                document.querySelector(`#like-count-${postId}`).innerHTML = data.likes;
                // Trigger animation
                this.classList.add('like-animated');
                setTimeout(() => {
                    this.classList.remove('like-animated');
                }, 300); // Duration of the animation
            });
        };
    });

});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}