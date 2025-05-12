from typing import List
from app.entities.agent_data import AgentData
from app.entities.processed_agent_data import ProcessedAgentData

ACCEL_HISTORY: List[float] = []
MAX_HISTORY_LENGTH = 10
EMA_ALPHA = 0.3  # smoothing factor: closer to 1 — less smoothed

# Thresholds to detect potholes and bumps based on z-axis acceleration changes
POTHOLE_DROP_THRESHOLD = -15.0  # strong drop in Z value
BUMP_PEAK_THRESHOLD = 15.0      # strong rise in Z value


def apply_ema(data: List[float], alpha: float) -> List[float]:
    """Applies exponential smoothing to a list of values."""
    if not data:
        return []

    smoothed = [data[0]]
    for value in data[1:]:
        new_val = alpha * value + (1 - alpha) * smoothed[-1]
        smoothed.append(new_val)
    return smoothed


def detect_event(data: List[float]) -> str:
    """Detect road event based on recent acceleration trend."""
    if len(data) < 3:
        return "normal"

    # Analyze last three points to detect sudden spike or dip
    v1, v2, v3 = data[-3:]

    delta1 = v2 - v1
    delta2 = v3 - v2

    if delta1 < POTHOLE_DROP_THRESHOLD and delta2 > abs(delta1) * 0.5:
        return "pothole"
    elif delta1 > BUMP_PEAK_THRESHOLD and delta2 < -abs(delta1) * 0.5:
        return "bump"
    else:
        return "normal"


def process_agent_data(agent_data: AgentData) -> ProcessedAgentData:
    """
    Process single agent data point and classify road surface condition
    using recent accelerometer Z-history.

    Args:
        agent_data (AgentData): Current agent data.

    Returns:
        ProcessedAgentData: Result with road surface classification.
    """
    global ACCEL_HISTORY

    z_value = agent_data.accelerometer.z
    ACCEL_HISTORY.append(z_value)

    if len(ACCEL_HISTORY) > MAX_HISTORY_LENGTH:
        ACCEL_HISTORY = ACCEL_HISTORY[-MAX_HISTORY_LENGTH:]

    # Smoothing the history before calculation
    smoothed_data = apply_ema(ACCEL_HISTORY, EMA_ALPHA)

    # Detect specific road event based on smoothed values
    road_state = detect_event(smoothed_data)

    return ProcessedAgentData(
        road_state=road_state,
        agent_data=agent_data
    )
