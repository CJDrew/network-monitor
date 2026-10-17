import altair as alt
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from store import store

st.set_page_config(layout="wide")
st.title("Network watcher")

TZ = ZoneInfo("America/Los_Angeles")

# label format, approx tick count, window, resample bucket (None = raw data)
TIMEFRAMES = {
    "5m":  ("%I:%M:%S", 6, timedelta(minutes=5),  None),
    "15m": ("%I:%M",    8, timedelta(minutes=15), None),
    "1h":  ("%I:%M",    6, timedelta(hours=1),    None),
    "6h":  ("%I:%M %p", 6, timedelta(hours=6),    "1min"),
    "1d":  ("%I:%M %p", 8, timedelta(days=1),     "5min"),
    "1w":  ("%a %d",    7, timedelta(weeks=1),    "30min"),
}


def _format_df(df, columns):
    return (
        df[columns]
        .reset_index()
        .melt(id_vars="timestamp", var_name="series", value_name="value")
    )


def _time_axis(timeframe, domain):
    fmt, tick_count, _, _ = TIMEFRAMES[timeframe]
    return alt.X(
        "timestamp:T",
        title=None,
        scale=alt.Scale(domain=[d.isoformat() for d in domain]),
        axis=alt.Axis(format=fmt, tickCount=tick_count, labelAngle=0),
    )


def _resample(df, bucket):
    if bucket is None:
        return df
    return df.resample(bucket).agg(
        {"avg_ms": "mean", "min_ms": "min", "max_ms": "max", "loss_pct": "max"}
    )


def latency_chart(df, columns, y_title, timeframe, domain):
    chart = (
        alt.Chart(_format_df(df, columns))
        .mark_line(clip=True)
        .encode(
            x=_time_axis(timeframe, domain),
            y=alt.Y("value:Q", title=y_title),
            color=alt.Color("series:N", title=None),
            tooltip=["timestamp:T", "series:N", "value:Q"],
        )
    )
    st.altair_chart(chart, use_container_width=True)


def loss_chart(df, columns, y_title, timeframe, domain):
    chart = (
        alt.Chart(_format_df(df, columns))
        .mark_line(clip=True)
        .encode(
            x=_time_axis(timeframe, domain),
            y=alt.Y("value:Q", title=y_title).scale(domain=[0, 100]),
            color=alt.Color("series:N", title=None),
            tooltip=["timestamp:T", "series:N", "value:Q"],
        )
    )
    st.altair_chart(chart, use_container_width=True)


@st.fragment(run_every="5s")
def dashboard():
    timeframe = st.segmented_control(
        "Timeframe", list(TIMEFRAMES), selection_mode="single", default="5m"
    )
    if timeframe is None:  # segmented_control returns None if the user deselects
        timeframe = "5m"

    _, _, window, bucket = TIMEFRAMES[timeframe]

    now = datetime.now(tz=TZ)
    start = now - window
    # Naive Pacific wall-clock times, matching the converted data below
    domain = (start.replace(tzinfo=None), now.replace(tzinfo=None))

    db = store("scan_results")
    df = db.get_observations(start.isoformat())

    if df.empty:
        st.info("No observations yet.")
        return

    df["timestamp"] = (
        pd.to_datetime(df["timestamp"], utc=True)
        .dt.tz_convert(TZ)
        .dt.tz_localize(None)
    )
    df = _resample(df.set_index("timestamp"), bucket)

    st.subheader("Latency (ms)")
    latency_chart(df, ["avg_ms", "min_ms", "max_ms"], "ms", timeframe, domain)

    st.subheader("Packet loss (%)")
    loss_chart(df, ["loss_pct"], "%", timeframe, domain)


dashboard()