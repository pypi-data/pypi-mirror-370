import time
import ping3


def main():
    target = input('請輸入目標 IP 位址|Enter target IP: ').strip()
    if not target:
        print('目標 IP 不可為空|Target IP cannot be empty')
        return

    try:
        interval_ms_str = input('請輸入 ping 間隔(ms)|Enter ping interval (ms): ').strip()
        interval_ms = int(interval_ms_str)
    except Exception:
        print('輸入無效，使用 100ms|Invalid input, using 100ms')
        interval_ms = 100

    if interval_ms < 1:
        print('最小間隔為 1ms，已自動調整|Minimum interval is 1ms; adjusted to 1ms')
        interval_ms = 1

    print(f"開始對 {target} 進行高速連續 Ping（Ctrl+C 結束）|Starting high-speed continuous ping to {target} (Ctrl+C to stop)")

    # Reduce DNS lookups by resolving once if needed; ping3 handles strings.
    # Use a short timeout to keep responsiveness; default to 1 second.
    timeout_s = 1.0
    interval_s = interval_ms / 1000.0

    sent = 0
    received = 0
    try:
        while True:
            start = time.perf_counter()
            sent += 1
            try:
                rtt = ping3.ping(target, timeout=timeout_s)
            except Exception:
                rtt = None

            if rtt is not None and rtt is not False:
                received += 1
                print(f"回應: {rtt*1000:.2f} ms|Reply: {rtt*1000:.2f} ms")
            else:
                print("逾時|Timeout")

            # Maintain interval
            elapsed = time.perf_counter() - start
            sleep_left = interval_s - elapsed
            if sleep_left > 0:
                time.sleep(sleep_left)
    except KeyboardInterrupt:
        loss = 0.0 if sent == 0 else (sent - received) * 100.0 / sent
        print("\n統計|Statistics")
        print(f"已發送: {sent} | Sent: {sent}")
        print(f"已接收: {received} | Received: {received}")
        print(f"遺失率: {loss:.1f}% | Packet Loss: {loss:.1f}%")


if __name__ == '__main__':
    main()
