# Name of the Environment variable to use for GitHub Tokens
ENV_GITHUB_TOKEN = "GH_ACCESS_TOKEN"

# GitHub has historically signed commits made via its web editor with a Key that expired in 2024
# The latest Key however has no expiration set. The "web-flow" Github account owns these keys:
# GitHub (web-flow commit signing) <noreply@github.com>
# https://api.github.com/users/web-flow/gpg_keys
GITHUB_WEB_EDITOR_SIGNING_KEYS = ['4AEE18F83AFDEB23', 'B5690EEEBB952194']

# This is ocd related, I needed my separators to match.
SCREEN_SEPARATOR_LENGTH = 100

REACTIONS_POSITIVE = ['+1', 'heart']
REACTIONS_NEGATIVE = ['-1']
REACTIONS_NEUTRAL = ['laugh', 'hooray', 'confused', 'rocket', 'eyes']

COMMIT_HOURS = {i: f"{i%12 if i%12 else 12}{'am' if i < 12 else 'pm'} UTC" for i in range(24)}

# Identifies user-supplied data as per: https://securitylab.github.com/resources/github-actions-untrusted-input/
WORKFLOWS_USER_INPUT = {
    "Issue Title": r'\${{\s*github\.event\.issue\.title\s*}}',
    "Issue Body": r'\${{\s*github\.event\.issue\.body\s*}}',
    "Pull Request Title": r'\${{\s*github\.event\.pull_request\.title\s*}}',
    "Pull Request Body": r'\${{\s*github\.event\.pull_request\.body\s*}}',
    "Comment Body": r'\${{\s*github\.event\.comment\.body\s*}}',
    "Review Body": r'\${{\s*github\.event\.review\.body\s*}}',
    "Review Comment Body": r'\${{\s*github\.event\.review_comment\.body\s*}}',
    "Page Name in Pages Event": r'\${{\s*github\.event\.pages(?:\.\w+|\[\d+\])\.page_name\s*}}',
    "Head Commit Message": r'\${{\s*github\.event\.head_commit\.message\s*}}',
    "Head Commit Author\'s Email": r'\${{\s*github\.event\.head_commit\.author\.email\s*}}',
    "Head Commit Author\'s Name": r'\${{\s*github\.event\.head_commit\.author\.name\s*}}',
    "Commit Author\'s Email": r'\${{\s*github\.event\.commits(?:\.\w+|\[\d+\])\.author\.email\s*}}',
    "Commit Author\'s Name": r'\${{\s*github\.event\.commits(?:\.\w+|\[\d+\])\.author\.name\s*}}',
    "Pull Request Head Ref": r'\${{\s*github\.event\.pull_request\.head\.ref\s*}}',
    "Pull Request Head Label": r'\${{\s*github\.event\.pull_request\.head\.label\s*}}',
    "Pull Request Default Branch": r'\${{\s*github\.event\.pull_request\.head\.repo\.default_branch\s*}}',
    "Head Ref": r'\${{\s*github\.head_ref\s*}}',
    "Inputs in Event": r'\${{\s*github\.event\.inputs(?:\.\w+|\[\w+\])\s*}}',
}

OPENPGP_SIG_TYPES = {
    0x00: "Signature of a binary document",
    0x01: "Signature of a canonical text document",
    0x02: "Standalone signature",
    0x10: "Generic certification of a User ID and Public-Key packet",
    0x11: "Persona certification of a User ID and Public-Key packet",
    0x12: "Casual certification of a User ID and Public-Key packet",
    0x13: "Positive certification of a User ID and Public-Key packet",
    0x18: "Subkey Binding Signature",
    0x19: "Primary Key Binding Signature",
    0x1F: "Signature directly on a key",
    0x20: "Key revocation signature",
    0x28: "Subkey revocation signature",
    0x30: "Certification revocation signature"
}

OPENPGP_PK_ALGOS = {
    1: "RSA (Encrypt or Sign)",
    2: "RSA Encrypt-Only",
    3: "RSA Sign-Only",
    16: "Elgamal Encrypt-Only",
    17: "DSA",
    18: "Reserved for Elliptic Curve",
    19: "Reserved for ECDSA",
    20: "Reserved (formerly Elgamal Encrypt or Sign)",
    21: "Reserved for Diffie-Hellman"
}

OPENPGP_HASH_ALGOS = {
    1: "MD5",
    2: "SHA-1",
    3: "RIPEMD-160",
    8: "SHA256",
    9: "SHA384",
    10: "SHA512",
    11: "SHA224"
}

