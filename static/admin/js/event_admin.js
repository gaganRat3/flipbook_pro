// Admin JavaScript for Event model
(function($) {
    $(document).ready(function() {
        // Check for similar event names when typing
        $('#id_name').on('input', function() {
            const eventName = $(this).val().trim();
            const warningDiv = $('#event-name-warning');
            
            // Remove existing warning
            warningDiv.remove();
            
            if (eventName.length > 2) {
                checkSimilarEventNames(eventName);
            }
        });

        function checkSimilarEventNames(eventName) {
            // Create warning div if it doesn't exist
            let warningDiv = $('#event-name-warning');
            if (warningDiv.length === 0) {
                warningDiv = $('<div id="event-name-warning" style="margin-top: 10px; padding: 10px; border-radius: 4px; display: none;"></div>');
                $('#id_name').closest('.form-row').append(warningDiv);
            }

            // Check for common event patterns
            const lowerName = eventName.toLowerCase();
            let suggestions = [];
            
            if (lowerName.includes('sammelan')) {
                suggestions.push('Consider using existing "Sammelan Events" if applicable');
            }
            
            if (lowerName.includes('event')) {
                suggestions.push('Check if a similar event already exists');
            }

            if (suggestions.length > 0) {
                showWarning(warningDiv, suggestions);
            } else {
                warningDiv.hide();
            }
        }

        function showWarning(warningDiv, suggestions) {
            const warningHtml = `
                <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; color: #856404;">
                    <strong>⚠️ Event Name Check:</strong>
                    <ul style="margin: 5px 0 0 20px;">
                        ${suggestions.map(s => `<li>${s}</li>`).join('')}
                    </ul>
                    <p style="margin: 5px 0 0 0; font-size: 0.9em;">
                        To avoid duplicate events, please check the existing events list before creating a new one.
                    </p>
                </div>
            `;
            warningDiv.html(warningHtml).show();
        }

        // Add helpful text to event selection in FlipBook admin
        if (window.location.pathname.includes('/books/flipbook/')) {
            addEventSelectionHelper();
        }

        function addEventSelectionHelper() {
            const eventSelect = $('#id_event');
            if (eventSelect.length > 0) {
                const helpText = $('<div class="help">Choose an existing event or create a new one. For "Sammelan" books, please use the existing "Sammelan Events" if available.</div>');
                eventSelect.closest('.form-row').append(helpText);
            }
        }
    });
})(django.jQuery);