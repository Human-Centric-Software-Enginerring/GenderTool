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
        document.getElementById('finalPrimaryContribution').textContent = stats.primaryContribution;
        document.getElementById('finalPrimaryContributionExtra').textContent = stats.primaryContributionExtra || '##';
        document.getElementById('finalTotalLinesOfCode').textContent = stats.totalLinesOfCode;
        document.getElementById('sessionLeadership').textContent = stats.sessionLeadership;
        document.getElementById('sessionLeadershipExtra').textContent = stats.sessionLeadershipExtra || '##';
        document.getElementById('finalCommunicationStyle').textContent = stats.communicationStyle;
        document.getElementById('finalCommunicationStyleExtra').textContent = stats.communicationStyleExtra || '##';
        document.getElementById('selfEfficacy').textContent = stats.selfEfficacy;
        document.getElementById('selfEfficacyExtra').textContent = stats.selfEfficacyExtra || '##';

        createPieChart('codeContributionChart', stats.codeContribution);
        createPieChart('communicationStyleChart', stats.communicationStats);

        document.getElementById('codeContributionYou').textContent = stats.codeContribution.You;
        document.getElementById('codeContributionPartner').textContent = stats.codeContribution.Partner;
        document.getElementById('communicationStyleVerbal').textContent = stats.communicationStats.Verbal;
        document.getElementById('communicationStyleNonVerbal').textContent = stats.communicationStats.NonVerbal;
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
            ctx.fillStyle = label === 'you' || label === 'verbal' ? '#ff0000' : '#0000ff';
            ctx.fill();
    
            // Add contrasting text
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
    
    // Add this line at the end of the script to ensure the charts are created when the page loads
    window.addEventListener('load', () => {
        createPieChart('codeContributionChart', {you: 50, partner: 50});
        createPieChart('communicationStyleChart', {verbal: 50, nonVerbal: 50});
    });
})();
