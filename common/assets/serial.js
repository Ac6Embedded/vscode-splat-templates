window.addEventListener('DOMContentLoaded', (event) => {
    const resizableBar = document.getElementById('resizable-bar');
    const board = document.getElementById('board');
    const uart = document.getElementById('uart');

    let isResizing = false;
    let startY;
    let startBoardHeight;
    let startUartHeight;

    resizableBar.addEventListener('mousedown', (event) => {
        isResizing = true;
        startY = event.clientY;
        startBoardHeight = board.getBoundingClientRect().height;
        startUartHeight = uart.getBoundingClientRect().height;

        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);
    });

    function handleMouseMove(event) {
        if (!isResizing) return;

        const diffY = event.clientY - startY;
        board.style.height = `${startBoardHeight + diffY}px`;
        uart.style.height = `${startUartHeight - diffY}px`;
    }

    function handleMouseUp() {
        if (isResizing) {
            isResizing = false;
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
        }
    }

    document.getElementById('refreshButton').addEventListener('click', function() {
        window.location.reload();
    });	
});

// View or hide serial send message 
function adjustUartHeight() {
    const footerHeight = 15; // Assuming 15px is the height you want to leave at the bottom
    const appHeight = document.getElementById('app').clientHeight; // Get the height of the outer container
    const resizableBarPosition = document.getElementById('resizable-bar').getBoundingClientRect().top; // Get the top position of the resizable bar
    const sendMessageContainer = document.getElementById('send-message-container');

    let heightAdjustment = footerHeight; // Start with the footer height

    // If the send-message-container is visible, add its height to the adjustment
    if (sendMessageContainer.style.display !== 'none') {
        heightAdjustment += sendMessageContainer.offsetHeight;
    }

    const newHeight = appHeight - resizableBarPosition - heightAdjustment; // Adjust new height calculation
    document.getElementById('uart').style.height = `${newHeight}px`; // Set the new height for the uart element
}

window.addEventListener('DOMContentLoaded', (event) => {
    const hideSerialButton = document.getElementById('hide-serial-button');
    const sendMessageContainer = document.getElementById('send-message-container');

    hideSerialButton.addEventListener('click', function() {
        // Toggle visibility by checking current display style
        if (sendMessageContainer.style.display === 'none') {
            sendMessageContainer.style.display = 'flex'; // Show it
            hideSerialButton.textContent = 'Hide';
        } else {
            sendMessageContainer.style.display = 'none'; // Hide it
            hideSerialButton.textContent = 'View';
        }
        adjustUartHeight(); // Adjust the height of the uart container
    });

    // Call this function on window resize to maintain proper layout
    window.addEventListener('resize', adjustUartHeight);

    // Initial adjustment on page load
    adjustUartHeight();
});
