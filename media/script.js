(function() {
    const vscode = acquireVsCodeApi();

    const hoverInfo = {
        primaryContribution: {
            navigator: "It can be a good idea to switch roles freely so that both you and your partner can have a fair say in the code.",
            driver: "It can be a good idea to switch roles freely so that both you and your partner can have a fair say in the code."
        },
        communicationStyle: {
            nonVerbal: "Make sure to listen and acknowledge what your partner says by responding verbally as well.",
            verbal: "Try to watch your partner's body language to see how they feel and understand them better."
        },
        partnerTrying: {
            working: "Continue focusing on the task, but remember to be friendly with your partner to build connection.",
            friendly: "Continue being friendly but remember to focus on the task at hand."
        },
    };

    const whyLinks = {
        primaryContribution: {
            navigator: "https://www.jstor.org/stable/26196132?seq=1",
            driver: "https://www.jstor.org/stable/26196132?seq=1"
        },
        communicationStyle: {
            verbal: "https://ieeexplore.ieee.org/document/9568912",
            nonVerbal: "https://academic.oup.com/joc/article-abstract/52/3/522/4110025?redirectedFrom=fulltext"
        },
        partnerTrying: {
            working: "https://dl.acm.org/doi/abs/10.1145/3498326",
            friendly: "https://dl.acm.org/doi/abs/10.1145/3498326"
        },
    };

    // Placeholder for interruptions over time data
    let interruptionsOverTime = {
        You: [0, 2, 5, 8, 10, 15, 18, 20, 22, 25, 28, 30],
        Partner: [0, 1, 3, 6, 9, 11, 14, 16, 19, 21, 24, 26]
    };

    // Info popups
    document.querySelectorAll('.info-icon').forEach(icon => {
        icon.addEventListener('click', function() {
            const popupType = this.id.replace('Info', '');
            showPopup(popupType);
        });
    });

    function showPopup(type) {
        const popup = document.getElementById('popup');
        const popupText = document.getElementById('popupText');
        const popupIcon = document.querySelector('.popup-icon');
        const whyLink = document.querySelector('.why-link');
        const toggle = document.getElementById(`${type}Toggle`);

        let state;
        let text;
        switch(type) {
            case 'primaryContribution':
                state = toggle.checked ? 'driver' : 'navigator';
                text = hoverInfo[type][state];
                break;
            case 'communicationStyle':
                state = toggle.checked ? 'nonVerbal' : 'verbal';
                text = hoverInfo[type][state];
                break;
            case 'partnerTrying':
                state = toggle.checked ? 'working' : 'friendly';
                text = hoverInfo[type][state];
                break;
            default:
                text = "No information available.";
        }

        popupText.textContent = text;
        popupIcon.innerHTML = '💡';
        whyLink.style.color = '#ff0000';
        whyLink.dataset.link = whyLinks[type][state] || whyLinks[type];
        popup.style.display = 'block';
    }

    document.querySelector('.close-btn').addEventListener('click', function() {
        document.getElementById('popup').style.display = 'none';
    });

    // Why link click handler
    document.querySelector('.why-link').addEventListener('click', function() {
        const link = this.dataset.link;
        if (link) {
            vscode.postMessage({
                command: 'openLink',
                link: link
            });
        }
    });

    // Toggle switches
    document.querySelectorAll('.toggle-input').forEach(toggle => {
        toggle.addEventListener('change', function() {
            const type = this.id.replace('Toggle', '');
            const value = this.checked ? 'ON' : 'OFF';
            vscode.postMessage({
                command: 'updateStat',
                type: type,
                value: value
            });
        });
    });

    // Handle messages from the extension
    window.addEventListener('message', event => {
        const message = event.data;
        switch (message.command) {
            case 'updateStats':
                document.getElementById('linesOfCode').textContent = message.linesOfCode;
                document.getElementById('interruptionCount').textContent = message.interruptionCount;
                document.getElementById('primaryContributionToggle').checked = message.primaryContribution === 'Driver';
                document.getElementById('communicationStyleToggle').checked = message.communicationStyle === 'Verbal';
                document.getElementById('partnerTryingToggle').checked = message.partnerTrying === 'Friendly';
                break;
            case 'updateFinalStats':
                updateFinalStats(message.stats);
                break;
        }
    });

    function updateFinalStats(stats) {
        const popup = document.getElementById('finalStatsPopup');
        const content = popup.querySelector('.final-stats-content');

        content.querySelector('#finalPrimaryContribution').textContent = stats.primaryContribution;
        content.querySelector('#finalTotalLinesOfCode').textContent = stats.totalLinesOfCode;
        content.querySelector('#sessionLeadership').textContent = stats.sessionLeadership;
        content.querySelector('#finalCommunicationStyle').textContent = stats.communicationStyle;
        content.querySelector('#selfEfficacy').textContent = stats.selfEfficacy;
        content.querySelector('#finalInterruptions').textContent = stats.interruptions;

        createPieChart('codeContributionChart', stats.codeContribution);
        createPieChart('communicationStyleChart', stats.communicationStats);
        createInterruptionsLineChart('interruptionsChart', stats.interruptionsOverTime || interruptionsOverTime);
    }

    function createPieChart(canvasId, data) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas element with id '${canvasId}' not found`);
            return;
        }
        const ctx = canvas.getContext('2d');
        const total = Object.values(data).reduce((a, b) => a + b, 0);
        let startAngle = 0;
    
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    
        Object.entries(data).forEach(([label, value]) => {
            const sliceAngle = (value / total) * 2 * Math.PI;
            ctx.beginPath();
            ctx.moveTo(100, 100);
            ctx.arc(100, 100, 100, startAngle, startAngle + sliceAngle);
            ctx.closePath();
            ctx.fillStyle = label === 'You' || label === 'Verbal' ? '#ff0000' : '#0000ff';
            ctx.fill();
    
            // Contrasting text
            const midAngle = startAngle + sliceAngle / 2;
            const x = 100 + Math.cos(midAngle) * 70;
            const y = 100 + Math.sin(midAngle) * 70;
            ctx.fillStyle = '#ffffff';
            ctx.font = '14px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(`${label}: ${Math.round(value)}%`, x, y);
    
            startAngle += sliceAngle;
        });
    }

    function createInterruptionsLineChart(canvasId, data) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas element with id '${canvasId}' not found`);
            return;
        }
        const ctx = canvas.getContext('2d');
        
        const maxInterruptions = 100;
        const maxMinutes = 60;
        const intervalMinutes = 5;
        
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        const legendWidth = 90;
        const chartWidth = canvas.width - 60 - legendWidth;
        const chartHeight = canvas.height - 60;
        const xStart = 50;
        const yStart = 10;
        
        // Draw axes
        ctx.beginPath();
        ctx.moveTo(xStart, yStart);
        ctx.lineTo(xStart, yStart + chartHeight);
        ctx.lineTo(xStart + chartWidth, yStart + chartHeight);
        ctx.strokeStyle = '#ffffff';
        ctx.stroke();
        
        ctx.fillStyle = '#ffffff';
        ctx.textAlign = 'right';
        ctx.textBaseline = 'middle';
        for (let i = 0; i <= maxInterruptions; i += 10) {
            const y = yStart + chartHeight - (i / maxInterruptions) * chartHeight;
            ctx.fillText(i.toString(), xStart - 5, y);
            ctx.beginPath();
            ctx.moveTo(xStart, y);
            ctx.lineTo(xStart + chartWidth, y);
            ctx.strokeStyle = '#333333';
            ctx.stroke();
        }
        
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        for (let i = 0; i <= maxMinutes; i += intervalMinutes) {
            const x = xStart + (i / maxMinutes) * chartWidth;
            ctx.fillText(i.toString(), x, yStart + chartHeight + 5);
            ctx.beginPath();
            ctx.moveTo(x, yStart);
            ctx.lineTo(x, yStart + chartHeight);
            ctx.strokeStyle = '#333333';
            ctx.stroke();
        }
        
        const drawLine = (dataPoints, color) => {
            ctx.beginPath();
            dataPoints.forEach((point, index) => {
                const x = xStart + (index * intervalMinutes / maxMinutes) * chartWidth;
                const y = yStart + chartHeight - (point / maxInterruptions) * chartHeight;
                if (index === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            });
            ctx.strokeStyle = color;
            ctx.lineWidth = 2;
            ctx.stroke();
        };
        
        drawLine(data.You, '#ff0000');
        drawLine(data.Partner, '#0000ff');

        ctx.fillStyle = '#ffffff';
        ctx.font = '14px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('Time (Minutes)', xStart + chartWidth / 2, yStart + chartHeight + 20);
        
        ctx.save();
        ctx.translate(15, yStart + chartHeight / 2);
        ctx.rotate(-Math.PI / 2);
        ctx.fillText('Interruptions', 0, 0);
        ctx.restore();

        const legendX = xStart + chartWidth + 20;
        const legendY = yStart + 20;
        const legendSpacing = 30;

        ctx.textAlign = 'left';
        ctx.textBaseline = 'middle';
        
        // You
        ctx.fillStyle = '#ff0000';
        ctx.fillRect(legendX, legendY, 20, 2);
        ctx.fillStyle = '#ffffff';
        ctx.fillText('You', legendX + 30, legendY);

        // Partner
        ctx.fillStyle = '#0000ff';
        ctx.fillRect(legendX, legendY + legendSpacing, 20, 2);
        ctx.fillStyle = '#ffffff';
        ctx.fillText('Partner', legendX + 30, legendY + legendSpacing);
    }
    
    // Final Stats button
    document.getElementById('finalStatsButton').addEventListener('click', showFinalStatsPopup);

    function showFinalStatsPopup() {
        const popup = document.getElementById('finalStatsPopup');
        popup.style.display = 'block';
    }

    // Close button for final stats popup
    document.querySelector('#finalStatsPopup .close-btn').addEventListener('click', function() {
        document.getElementById('finalStatsPopup').style.display = 'none';
    });

    // Ensuring the charts are created when the page loads
    window.addEventListener('load', () => {
        createPieChart('codeContributionChart', {You: 50, Partner: 50});
        createPieChart('communicationStyleChart', {Verbal: 50, NonVerbal: 50});
        createInterruptionsLineChart('interruptionsChart', interruptionsOverTime);
    });
})();
