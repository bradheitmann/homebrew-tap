class Minimux < Formula
  desc "Daemon for agent-owned PTY sessions with crash-recoverable terminal state"
  homepage "https://github.com/bradheitmann/minimux"
  license "Apache-2.0"

  on_macos do
    on_arm do
      url "https://github.com/bradheitmann/minimux/releases/download/v0.2.0/minimux-v0.2.0-aarch64-macos.tar.gz"
      sha256 "258d0a7970baa554df39f2a8a7f69234216b411946d8bc784ae9fee727aafa05"
    end
    on_intel do
      url "https://github.com/bradheitmann/minimux/releases/download/v0.2.0/minimux-v0.2.0-x86_64-macos.tar.gz"
      sha256 "023be27d7002aa5bf9d84e10cd283657a33d47978160ee622563529543142eed"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/bradheitmann/minimux/releases/download/v0.2.0/minimux-v0.2.0-aarch64-linux.tar.gz"
      sha256 "4b320c3b7789f5c9749e39839a9d90645017a1c26d94e006789c45046be8572f"
    end
    on_intel do
      url "https://github.com/bradheitmann/minimux/releases/download/v0.2.0/minimux-v0.2.0-x86_64-linux.tar.gz"
      sha256 "e8ab5b205e930617d0e9ecb1bcd3b41085ee9908662ff1c56b3b3960160025c7"
    end
  end

  def install
    bin.install "minimux"
    doc.install "README.md", "SPEC-v2.2.md"
    (doc/"docs").install Dir["docs/*"]
  end

  test do
    output = shell_output("#{bin}/minimux --json system.health")
    assert_match '"product":"minimux"', output
    assert_match '"version":"0.2.0"', output
  end
end
