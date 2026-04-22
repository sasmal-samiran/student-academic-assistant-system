const backendApi = "http://127.0.0.1:8000";

const chatBody = document.getElementById("chat-body");
const userInput = document.getElementById("user-input");

async function sendMessage() {
    const message = userInput.value.trim();
    if (message === "") return;
    addMessage(message, "user");
    userInput.value = "";
    showTypingIndicator();
    const reply = await generateReply(message);
    removeTypingIndicator();
    if (reply.bot_reply != null) {
        addMessage(reply.bot_reply, "bot");
    }
    else if (reply.bot_reply.includes("SELECT")) {
        addMessage("server is taking too, please try again", "bot");
    } else {
        addMessage("Sorry, please try again!", "bot");
    }
    if (reply.attendance_record) {
        addAttendanceChart(reply.attendance_record);
    } else if (reply.predicted_attendance_record) {
        addPredictedAttendanceChart(reply.predicted_attendance_record);
    } else if (reply.chart_config) {
        renderChart(reply.chart_config);
    }
    else {
        removeDashboard();
    }
}

function handleKeyPress(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}

function addMessage(text, sender) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", sender);

    const bubble = document.createElement("div");
    bubble.classList.add("bubble");

    // Use innerHTML for bot, innerText for user
    if (sender === "bot") {
        bubble.innerHTML = text;
    } else {
        bubble.innerText = text;
    }

    messageDiv.appendChild(bubble);
    chatBody.appendChild(messageDiv);
    chatBody.scrollTop = chatBody.scrollHeight;
}

function showTypingIndicator() {
    if (document.getElementById("typing")) return;

    const typingDiv = document.createElement("div");
    typingDiv.classList.add("message", "bot");
    typingDiv.id = "typing";

    const bubble = document.createElement("div");
    bubble.classList.add("bubble", "listening-bubble");

    // 🔥 Use span with class "dots"
    bubble.innerHTML = `Typing<span class="dots"></span>`;

    typingDiv.appendChild(bubble);
    chatBody.appendChild(typingDiv);
    chatBody.scrollTop = chatBody.scrollHeight;
}

function removeTypingIndicator() {
    const typing = document.getElementById("typing");
    if (typing) typing.remove();
}

let mediaRecorder;
let audioChunks = [];
let isRecording = false;

function showListeningIndicator() {
    if (document.getElementById("listening-indicator")) return;

    const indicator = document.createElement("div");
    indicator.id = "listening-indicator";
    indicator.classList.add("message", "user");

    const bubble = document.createElement("div");
    bubble.classList.add("bubble", "listening-bubble");
    bubble.innerHTML = `🎙️ Listening<span class="dots"></span>`;

    indicator.appendChild(bubble);
    chatBody.appendChild(indicator);
    chatBody.scrollTop = chatBody.scrollHeight;
}

function removeListeningIndicator() {
    const indicator = document.getElementById("listening-indicator");
    if (indicator) indicator.remove();
}
async function toggleVoice() {
    const btn = document.getElementById("voice-btn");

    if (!isRecording) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };

            mediaRecorder.start();
            isRecording = true;

            btn.innerText = "⏹️";
            showListeningIndicator();
        } catch (err) {
            alert("Mic access denied")
        }

    } else {
        mediaRecorder.stop();
        isRecording = false;
        btn.innerText = "🎤";
        removeListeningIndicator();

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: "audio/webm" });

            showTypingIndicator();
            const reply = await generateReply(null, audioBlob);
            removeTypingIndicator();

            addMessage(reply.user_query, "user");
            if (reply.bot_reply != null) {
                addMessage(reply.bot_reply, "bot");
            }
            else if (reply.bot_reply.includes("SELECT")) {
                addMessage("server is taking too, please try again", "bot");
            } else {
                addMessage("Sorry, please try again!", "bot");
            }
            if (reply.attendance_record) {
                addAttendanceChart(reply.attendance_record);
            } else if (reply.predicted_attendance_record) {
                addPredictedAttendanceChart(reply.predicted_attendance_record);
            } else if (reply.chart_config) {
                renderChart(reply.chart_config);
            }
            else {
                removeDashboard();
            }
        };
    }
}

function addDashboardChartContainer() {
    const container = document.body; // ✅ correct

    // 🔥 Remove old dashboard if exists
    const oldDashboard = document.getElementById("dashboard");
    if (oldDashboard) oldDashboard.remove();

    // 🔹 Create dashboard div
    const dashboardDiv = document.createElement("div");
    dashboardDiv.classList.add("dashboard");
    dashboardDiv.id = "dashboard";

    // 🔹 Create canvas
    const canvas = document.createElement("canvas");
    canvas.id = "predictionChart";

    dashboardDiv.appendChild(canvas);
    container.prepend(dashboardDiv);
    setTimeout(() => {
        dashboardDiv.classList.add("show");
    }, 50);

    return canvas.id;
}
function removeDashboard() {
    const dashboard = document.getElementById("dashboard");

    if (dashboard) {
        dashboard.remove();
    }
    if (predictionChart) {
        predictionChart.destroy();
        predictionChart = null;
    }
}

function renderChart(config) {
    const canvasId = addDashboardChartContainer();

    const canvas = document.getElementById("predictionChart");
    if (!canvas) return;

    if (predictionChart) predictionChart.destroy();
    let parsed;
    try {
        parsed = typeof config === "string" ? JSON.parse(config) : config;

        parsed.options = parsed.options || {};
        parsed.options.plugins = parsed.options.plugins || {};

        parsed.options.plugins.title = {
            display: true,
            text: parsed.title || "Chart",
            color: "#ffffff",
            font: {
                size: 16,
                weight: "bold"
            }
        };
        predictionChart = new Chart(canvas, {
            type: parsed.type,
            data: parsed.data,
            options: parsed.options
        });
    } catch (e) {
        console.error("Error: ", e);
        return;
    }
}

let predictionChart;
Chart.register(ChartDataLabels);
Chart.defaults.color = "#ffffff";
function addAttendanceChart(data) {
    if (!data || !data.attendance) {
        console.error("Invalid attendance data", data);
        return;
    }
    const canvasId = addDashboardChartContainer();
    if (document.getElementById("predictionChart")) {
        if (predictionChart) predictionChart.destroy();
        predictionChart = new Chart(document.getElementById("predictionChart"), {
            type: "bar",
            data: {
                labels: data.subject_name,
                datasets: [{
                    label: "Attendance %",
                    data: data.attendance,
                    backgroundColor: data.attendance.map(a =>
                        (!a || isNaN(a)) ? "#9E9E9E" : (a < 75 ? "#f73939" : "#05db5b")
                    )
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true, labels: {
                            color: "#ffffff"
                        }
                    },
                    tooltip: {
                        titleColor: "#ffffff",
                        bodyColor: "#ffffff"
                    },
                    datalabels: {
                        anchor: 'center',
                        align: 'center',
                        formatter: (value) => value + "%",
                        color: "#ffffff",
                        font: {
                            weight: 'bold'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: "#ffffff" // X-axis labels
                        },
                        border: {
                            color: "#ffffff" // X-axis line
                        },
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            color: "#ffffff" // Y-axis labels
                        },
                        border: {
                            color: "#ffffff" // X-axis line
                        },
                        grid: {
                            display: false
                        }
                    }

                }
            }
        });
    }
}

function addPredictedAttendanceChart(data) {
    if (!data || !data.predicted_attendance || !data.attendance) {
        console.error("Invalid attendance data", data);
        return;
    }
    const canvasId = addDashboardChartContainer();
    if (document.getElementById("predictionChart")) {
        if (predictionChart) predictionChart.destroy();
        predictionChart = new Chart(document.getElementById("predictionChart"), {
            type: "bar",
            data: {
                labels: data.subject_name,
                datasets: [
                    {
                        label: "Current %",
                        data: data.attendance,
                        backgroundColor: "#2196F3"
                    },
                    {
                        label: "Predicted %",
                        data: data.predicted_attendance,
                        backgroundColor: "#4CAF50"
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,

                plugins: {
                    legend: {
                        labels: {
                            color: "#ffffff"
                        }
                    },
                    datalabels: {
                        anchor: 'center',
                        align: 'center',
                        formatter: (value) => value + "%",
                        color: "#ffffff",
                        font: {
                            weight: "bold"
                        }
                    },
                    annotation: {
                        annotations: {
                            line1: {
                                type: 'line',
                                yMin: 75,
                                yMax: 75,
                                borderColor: 'yellow',
                                borderWidth: 2,
                                label: {
                                    content: '75% Target',
                                    enabled: true
                                }
                            }
                        }
                    }
                },

                scales: {
                    x: {
                        ticks: {
                            color: "#ffffff"
                        },
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            color: "#ffffff"
                        },
                        grid: {
                            display: false
                        }
                    }
                },

                animation: {
                    duration: 1200,
                    easing: "easeOutQuart"
                }
            }
        });
    }
}

async function generateReply(message = null, audioBlob = null) {
    let textMessage = message || document.getElementById("user-input").value;
    if (!textMessage && !audioBlob) return "No input provided.";
    try {
        const formData = new FormData();
        if (audioBlob) {
            formData.append("audio", audioBlob, "voice.webm");
        }
        if (textMessage && !audioBlob) {
            formData.append("text", textMessage);
        }

        const response = await axios.post(`${backendApi}/ai_engine`, formData, {
            headers: {
                "Content-Type": "multipart/form-data"
            }
        });
        return response.data;
    } catch (error) {
        console.log(error);
        if (error.response) { alert("Session restarted. Please try again."); }
        else if (error.request) { alert("Server not responding."); }
        else { alert("Something went wrong."); }
    }
}