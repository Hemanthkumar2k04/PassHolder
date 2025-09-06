"""
Animation frames for PassHolder loading animation
Cross-platform ASCII art frames
"""

ANIMATION_FRAMES = [
    # Frame 1: LOCKED
    """
    ╔══════════════════════════════════════╗
    ║            PASSHOLDER                ║
    ║         Secure Password DB           ║
    ╠══════════════════════════════════════╣
    ║                                      ║
    ║    [LOCK] [████████████████████████] ║
    ║                                      ║
    ║         Status: LOCKED               ║
    ║                                      ║
    ╚══════════════════════════════════════╝
    """,
    # Frame 2: Starting to unlock
    """
    ╔══════════════════════════════════════╗
    ║            PASSHOLDER                ║
    ║         Secure Password DB           ║
    ╠══════════════════════════════════════╣
    ║                                      ║
    ║   [LOCK*] [███████████████████████▓] ║
    ║                                      ║
    ║         Status: AUTHENTICATING...    ║
    ║                                      ║
    ╚══════════════════════════════════════╝
    """,
    # Frame 3: Quarter unlocked
    """
    ╔══════════════════════════════════════╗
    ║            PASSHOLDER                ║
    ║         Secure Password DB           ║
    ╠══════════════════════════════════════╣
    ║                                      ║
    ║   [UNLK*] [██████████████████▓▓▓▓▓▓] ║
    ║                                      ║
    ║         Status: DECRYPTING...        ║
    ║                                      ║
    ╚══════════════════════════════════════╝
    """,
    # Frame 4: Half unlocked
    """
    ╔══════════════════════════════════════╗
    ║            PASSHOLDER                ║
    ║         Secure Password DB           ║
    ╠══════════════════════════════════════╣
    ║                                      ║
    ║   [UNLK*] [████████████▓▓▓▓▓▓▓▓▓▓▓▓] ║
    ║                                      ║
    ║         Status: UNLOCKING...         ║
    ║                                      ║
    ╚══════════════════════════════════════╝
    """,
    # Frame 5: Three quarters unlocked
    """
    ╔══════════════════════════════════════╗
    ║            PASSHOLDER                ║
    ║         Secure Password DB           ║
    ╠══════════════════════════════════════╣
    ║                                      ║
    ║   [UNLCK] [██████▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓] ║
    ║                                      ║
    ║         Status: LOADING...           ║
    ║                                      ║
    ╚══════════════════════════════════════╝
    """,
    # Frame 6: Almost unlocked
    """
    ╔══════════════════════════════════════╗
    ║            PASSHOLDER                ║
    ║         Secure Password DB           ║
    ╠══════════════════════════════════════╣
    ║                                      ║
    ║   [OPEN*] [███▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓] ║
    ║                                      ║
    ║         Status: FINALIZING...        ║
    ║                                      ║
    ╚══════════════════════════════════════╝
    """,
    # Frame 7: Completely unlocked
    """
    ╔══════════════════════════════════════╗
    ║            PASSHOLDER                ║
    ║         Secure Password DB           ║
    ╠══════════════════════════════════════╣
    ║                                      ║
    ║   [OPEN]  [░░░░░░░░░░░░░░░░░░░░░░░░] ║
    ║                                      ║
    ║         Status: UNLOCKED             ║
    ║                                      ║
    ╚══════════════════════════════════════╝
    """,
    # Frame 8: Ready state
    """
    ╔══════════════════════════════════════╗
    ║            PASSHOLDER                ║
    ║         Secure Password DB           ║
    ╠══════════════════════════════════════╣
    ║  [DIR] Passwords Ready:              ║
    ║    • Database: Decrypted             ║
    ║    • Access: Granted                 ║
    ║    • Security: Active                ║
    ║                                      ║
    ║         Status: READY                ║
    ╚══════════════════════════════════════╝
    """,
]

# Animation timing
FRAME_DURATION = 0.25  # seconds per frame (faster for smoother animation)
TOTAL_ANIMATION_TIME = len(ANIMATION_FRAMES) * FRAME_DURATION
