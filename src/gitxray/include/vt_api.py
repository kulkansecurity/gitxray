import os, time, requests

class VTRESTAPI:
    def __init__(self, gx_output):
        self.gx_output = gx_output
        self.VT_API_URL = "https://www.virustotal.com/api/v3"
        self.VT_API_KEY = os.environ.get("VT_API_KEY", None)

        self._PRIVATE_RANGES = [
            (0x0A000000, 0x0AFFFFFF),  # 10.0.0.0/8
            (0xAC100000, 0xAC1FFFFF),  # 172.16.0.0/12
            (0xC0A80000, 0xC0A8FFFF),  # 192.168.0.0/16
            (0x7F000000, 0x7FFFFFFF),  # 127.0.0.0/8       (loopback)
            (0xA9FE0000, 0xA9FEFFFF),  # 169.254.0.0/16    (link-local)
            (0xE0000000, 0xEFFFFFFF),  # 224.0.0.0/4       (multicast)
            (0xF0000000, 0xFFFFFFFE),  # 240.0.0.0/4       (reserved)
        ]


    def vt_request_json(self, url, max_retries=3):
        headers = {"x-apikey": self.VT_API_KEY, "accept": "application/json"}
        for attempt in range(1, max_retries + 1):
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", 60))
                self.gx_output.notify(f"\r[VirusTotal] rate limited [you may have met your daily quota]: sleeping {retry_after}s (try {attempt}/{max_retries})")
                time.sleep(retry_after)
                continue
            if resp.status_code == 401:
                self.gx_output.warn(f"\r[VirusTotal] VT_API_KEY may be incorrect, getting unauthorized errors.")
                break
            resp.raise_for_status()
        return None
        #raise RuntimeError(f"VT API retries exceeded for {url}")

    def _ipv4_to_int(self, ip_str):
        parts = ip_str.split('.')
        if len(parts) != 4:
            raise ValueError(f"Invalid IPv4 address: {ip_str!r}")
        n = 0
        for p in parts:
            if not p.isdigit():
                raise ValueError(f"Invalid IPv4 octet: {p!r}")
            x = int(p)
            if x < 0 or x > 255:
                raise ValueError(f"IPv4 octet out of range: {p!r}")
            n = (n << 8) | x
        return n

    def is_private_ipv4(self, ip_str):
        """
        Returns True if ip_str falls into any of the non-routable IPv4 blocks,
        or is the unspecified address 0.0.0.0.
        """
        n = self._ipv4_to_int(ip_str)
        if n == 0x00000000:
            return True
        for start, end in self._PRIVATE_RANGES:
            if start <= n <= end:
                return True
        return False

    def is_ip_address(self, host: str) -> bool:
        # True if every character is a digit or a dot
        return bool(host) and all(c.isdigit() or c == '.' for c in host)

    def is_testable(self, host):
        known_hosts = ["github.com","raw.github.com","api.github.com","gitlab.com","www.google.com","docs.google.com","sheets.google.com","google.com","python.org"]
        return "." in host and host not in known_hosts

    def host_report(self, domain, debug_enabled=False):
        if self.VT_API_KEY:
            try:
                if not self.is_testable(domain): return None
                if not self.is_ip_address(domain):
                    return self.vt_request_json(f"{self.VT_API_URL}/domains/{domain}")
                elif not self.is_private_ipv4(domain):
                    return self.vt_request_json(f"{self.VT_API_URL}/ip_addresses/{domain}")
            except Exception as ex:
                if debug_enabled: print(ex)
                else: pass

        return None
