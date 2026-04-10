import json, uuid, sys, time
import requests
from pathlib import Path

AI_URL = "http://localhost:8000/ai/conversation"
CASES_PATH = Path(__file__).resolve().parents[1] / "evaluation" / "test_cases.json"

def run_case(case):
    call_sid = f"EVAL-{case['id']}-{uuid.uuid4().hex[:6]}"
    turns = case["turns"]
    last_resp = None
    ok = True
    errors = []
    turn_count = 0

    for t in turns:
        payload = {
            "callSid": call_sid,
            "customerMessage": {
                "speaker": "customer",
                "message": t,
                "startedAt": "eval"
            }
        }
        r = requests.post(AI_URL, json=payload, timeout=10)
        last_resp = r.json()
        turn_count += 1

        # 可选：打印每一步（hack demo 时可开）
        # print(case["id"], ">>", t, "=>", last_resp.get("step"))

        # 防御：接口异常
        if "step" not in last_resp:
            ok = False
            errors.append("no_step_in_response")
            break

    expect = case.get("expect", {})
    exp_step = expect.get("step")
    exp_hangup = expect.get("shouldHangup")
    req_booking_id = expect.get("requireBookingId", False)

    if exp_step is not None and last_resp.get("step") != exp_step:
        ok = False
        errors.append(f"step_mismatch(exp={exp_step}, got={last_resp.get('step')})")

    if exp_hangup is not None and last_resp.get("shouldHangup") != exp_hangup:
        ok = False
        errors.append(f"hangup_mismatch(exp={exp_hangup}, got={last_resp.get('shouldHangup')})")

    booking_id = last_resp.get("bookingId") or (last_resp.get("extractedInfo") or {}).get("bookingId")
    if req_booking_id and not booking_id:
        ok = False
        errors.append("missing_bookingId")

    # 字段完整率（只做统计，不作为 hard fail）
    extracted = last_resp.get("extractedInfo") or {}
    missing_fields = [k for k in ["customerName","phoneNumber","address","serviceName","bookingTime"] if not extracted.get(k)]

    return {
        "id": case["id"],
        "ok": ok,
        "turns": turn_count,
        "errors": errors,
        "bookingId": booking_id,
        "missingFields": missing_fields,
        "finalStep": last_resp.get("step"),
        "finalHangup": last_resp.get("shouldHangup"),
    }

def main():
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    results = [run_case(c) for c in cases]

    total = len(results)
    passed = sum(1 for r in results if r["ok"])
    success_rate = passed / total * 100

    avg_turns = sum(r["turns"] for r in results) / total

    booking_ok = sum(1 for r in results if r["bookingId"])
    booking_rate = booking_ok / total * 100

    field_complete = sum(1 for r in results if len(r["missingFields"]) == 0)
    field_complete_rate = field_complete / total * 100

    print("\n==== Dispatch-AI Evaluation Report ====")
    print(f"Total cases: {total}")
    print(f"Passed: {passed} ({success_rate:.1f}%)")
    print(f"Avg turns per case: {avg_turns:.2f}")
    print(f"BookingId generated: {booking_ok}/{total} ({booking_rate:.1f}%)")
    print(f"All fields complete: {field_complete}/{total} ({field_complete_rate:.1f}%)")

    failed = [r for r in results if not r["ok"]]
    if failed:
        print("\n---- Failed cases ----")
        for r in failed:
            print(f"{r['id']}: errors={r['errors']} finalStep={r['finalStep']} hangup={r['finalHangup']}")
    else:
        print("\nAll cases passed ✅")

    # 可选：输出详细 JSON
    out_path = Path(__file__).resolve().parents[1] / "evaluation" / "eval_results.json"
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nDetailed results saved to: {out_path}")

if __name__ == "__main__":
    main()
