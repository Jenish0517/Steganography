# Steganography
 Built a steganography web application to safely insert and retrieve secret  messages in image, audio, and video files through LSB and associated  methods, allowing private data transfer with imperceptible modifications in  the media.
 
 Project Overview

This project provides a user-friendly web interface and an API to encode (hide) and decode (retrieve) secret messages inside media files (PNG/JPEG images, WAV/MP3 audio, and MP4/MKV video) using LSB-based steganography and associated pre-/post-processing techniques. The goal is to enable private data transfer while keeping visual and auditory quality intact.

Key goals:

Imperceptible embedding of messages

Support for multiple media types (image, audio, video)

Optional encryption and compression prior to embedding

Metadata and integrity checks to detect tampering

Simple REST API and web UI for non-technical users

Features

Media formats supported: PNG, BMP, JPG (lossy with caveats), WAV, FLAC, MP3 (limited), MP4, MKV

Embedding methods: LSB (single-bit, multi-bit), adaptive LSB (payload-aware), frame-based LSB for video

Preprocessing: optional AES-256 encryption, GZIP compression

Postprocessing: HMAC verification, checksum, length header

User interface: drag-and-drop upload, preview, progress indicators

APIs: REST endpoints for encode/decode with JSON responses

Security: password-based encryption, rate limits, file size limits

Audit & logging: store operation logs (no secret content), optional ephemeral mode

Threat Model & Security Considerations

Adversaries: passive observers (traffic/file inspection), naive active attackers (file modification), not designed to resist forensic experts or powerful state actors.

Confidentiality: Achieved when encryption is enabled (recommended). LSB alone provides secrecy by obscurity, not cryptographic confidentiality.

Integrity: HMAC and checksums detect accidental corruption and many tampering attempts.

Best practices: always use a strong secret/passphrase for encryption, prefer lossless formats (PNG, WAV, FLAC), and avoid embedding large payloads in lossy formats (JPEG, MP3) unless using error-resilient schemes.
