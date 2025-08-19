// Functions for handling message indentation based on parent relationships

function getParentCount(messageContent) {
    // Extract Parent_Ids from the first line of message content
    const firstLine = messageContent.split('\n')[0];
    const parentMatch = firstLine.match(/Parent_Ids:\s*([^)]+)/);
    
    if (!parentMatch) {
        return 0;
    }
    
    // Extract the X-Y-Z part and count dashes
    const idsOnly = parentMatch[1].trim();
    return (idsOnly.match(/-/g) || []).length + 1;
}

function calculateMarginShift(parentCount) {
    return Math.min(parentCount * 4, 20);
}

function applyMessageIndentation(messageElement) {
    if (!messageElement) {
        return;
    }
    // Indentation for user-message
    if (messageElement.classList.contains('user-message')) {
        messageElement.style.marginLeft = `20%`;
        messageElement.style.marginRight = `0%`;
    } 
    // Indentation for agent-message
    else {
        const content = messageElement.textContent || '';
        const parentCount = getParentCount(content);
        const marginLeft = calculateMarginShift(parentCount);
        const marginRight = 20 - calculateMarginShift(parentCount);
        messageElement.style.marginLeft = `${marginLeft}%`;
        messageElement.style.marginRight = `${marginRight}%`;
    }
}

// Export functions for use in other modules
window.chatIndentation = {
    getParentCount,
    calculateMarginShift,
    applyMessageIndentation
};