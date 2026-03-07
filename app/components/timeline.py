from datetime import datetime
import streamlit.components.v1 as components
from db.queries.timeline import fetch_career_timeline




def compute_timeline_positions(events):
    def parse(date_str):
        return datetime.now() if date_str == "present" else datetime.strptime(date_str, "%Y-%m")

    starts = [parse(e["start"]) for e in events]
    ends = [parse(e["end"]) for e in events]

    global_start = min(starts)
    global_end = max(ends)
    total_span = (global_end - global_start).days

    durations = []

    for e in events:
        duration_days = (parse(e["end"]) - parse(e["start"])).days
        durations.append(duration_days)

    min_dur = min(durations)
    max_dur = max(durations)

    positioned = []

    for e, dur in zip(events, durations):
        start_pct = ((parse(e["start"]) - global_start).days / total_span) * 100
        end_pct = ((parse(e["end"]) - global_start).days / total_span) * 100

        # --- Normalize dot size (8px → 18px range)
        if max_dur == min_dur:
            dot_size = 12
        else:
            dot_size = 16 + (dur - min_dur) / (max_dur - min_dur) * 18

        positioned.append({
            **e,
            "start_pct": round(start_pct, 2),
            "end_pct": round(end_pct, 2),
            "dot_size": round(dot_size, 1),
            "start_year": parse(e["start"]).year,
            "end_year": "Present" if e["end"] == "present" else parse(e["end"]).year
                })

    return positioned


def render_career_timeline():
    events = fetch_career_timeline()
    timeline = compute_timeline_positions(events)

    # base_height = 160          # header + base spacing
    # per_event_height = 40      # safe vertical buffer
    # iframe_height = base_height + len(events) * per_event_height

    components.html(
        f"""
        <style>

        .timeline-card {{
            background: #f9fafb;               /* same as exp-card */
            border-radius: 16px;
            padding: 14px 1.8rem;              /* slightly tighter */
            box-shadow: 0 10px 26px rgba(0,0,0,0.08);
            border-left: 4px solid #1f2937;     /* anchor */
            margin-bottom: 1.8rem;
        }}


        .timeline-wrapper {{
            font-family: system-ui;
            margin-bottom: 0.8rem;
        }}

        .timeline-line {{
            position: relative;
            height: 10px;
            background: #d1d5db;
            border-radius: 4px;
            margin: 1.8rem 0 1.6rem 0;
        }}

        .timeline-segment {{
            position: absolute;
            height: 10px;
            border-radius: 6px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.25);
        }}

        .education {{
            background: #60a5fa;
        }}

        .experience {{
            background: #1f2937;
        }}

        .timeline-label {{
            position: absolute;
            top: -2.2rem;
            font-size: 0.75rem;
            color: #374151;
            transform: translateX(-50%);
            white-space: nowrap;
        }}

        .timeline-dot {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            border-radius: 100%;
            background: #111827;
            box-shadow: 0 2px 8px rgba(0,0,0,0.35);
        }}

        .education .timeline-dot {{
            background: #3b82f6;
        }}
        
        .timeline-year {{
            position: absolute;
            top: 18px;
            font-size: 0.7rem;
            color: #374151;
            opacity: 0.85;
            white-space: nowrap;
        }}

        .start-year {{
            left: 0;
            transform: translateX(-10%);
        }}

        .end-year {{
            right: 0;
            transform: translateX(10%);
        }}

        /* Running education feels active */
        .education .end-year {{
            font-weight: 600;
            color: #2563eb;
        }}


        </style>

        <div class="timeline-card">
            <h3>Career Timeline</h3>

            <div class="timeline-wrapper">
                <div class="timeline-line">
                    {"".join([
                        f'''
                        <div class="timeline-segment {e['type']}"
                            style="
                                left:{e['start_pct']}%;
                                width:{e['end_pct'] - e['start_pct']}%;
                            ">

                            <!-- Dot (duration-sized, centered) -->
                            <div class="timeline-dot"
                                style="
                                    width:{e['dot_size']}px;
                                    height:{e['dot_size']}px;
                                ">
                            </div>

                            <!-- Role label -->
                            <div class="timeline-label" style="left:50%">
                                {e['label']}
                            </div>

                            <!-- Start year -->
                            <div class="timeline-year start-year">
                                {e['start_year']}
                            </div>

                            <!-- End year / Present -->
                            <div class="timeline-year end-year">
                                {e['end_year']}
                            </div>

                        </div>
                        '''
                        for e in timeline
                    ])}
                </div>
            </div>
        </div>

        """,
        height=150,
        scrolling=False
    )
