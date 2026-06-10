class Minimux < Formula
  desc "Daemon for agent-owned PTY sessions with crash-recoverable terminal state"
  homepage "https://github.com/bradheitmann/minimux"
  version "0.1.0"
  license "Apache-2.0"

  on_macos do
    on_arm do
      url "https://github.com/bradheitmann/minimux/releases/download/v0.1.0/minimux-v0.1.0-aarch64-macos.tar.gz"
      sha256 "a90213aa83eac735d4a8d28ef627476f9ab12678d1c82dbd91cb0d3c5a9aca99"
    end
    on_intel do
      url "https://github.com/bradheitmann/minimux/releases/download/v0.1.0/minimux-v0.1.0-x86_64-macos.tar.gz"
      sha256 "2fd4f3584031349fa64da0629e909f0719a8f1a4eb1697cdf8ec28f40333c65a"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/bradheitmann/minimux/releases/download/v0.1.0/minimux-v0.1.0-aarch64-linux.tar.gz"
      sha256 "ee72370a9ba72cdabfa911ab2e66c6eb58668786eadc12865d5dc076ff894ace"
    end
    on_intel do
      url "https://github.com/bradheitmann/minimux/releases/download/v0.1.0/minimux-v0.1.0-x86_64-linux.tar.gz"
      sha256 "cc11526487d1f742a99f5aedbf2412194385cf43bf40585f5c6802b11862ec10"
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
    assert_match '"version":"0.1.0"', output
  end
end
