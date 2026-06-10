class Minimux < Formula
  desc "Daemon for agent-owned PTY sessions with crash-recoverable terminal state"
  homepage "https://github.com/bradheitmann/minimux"
  license "Apache-2.0"

  on_macos do
    on_arm do
      url "https://github.com/bradheitmann/minimux/releases/download/v0.1.1/minimux-v0.1.1-aarch64-macos.tar.gz"
      sha256 "b136ca4b3fd4c315dd0312411da5191a9213b9f305187b764fe2d0314beea3c5"
    end
    on_intel do
      url "https://github.com/bradheitmann/minimux/releases/download/v0.1.1/minimux-v0.1.1-x86_64-macos.tar.gz"
      sha256 "4669529ece3a2b9196370830ca91e884d539bcd66843345f5f1e00cda17ce601"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/bradheitmann/minimux/releases/download/v0.1.1/minimux-v0.1.1-aarch64-linux.tar.gz"
      sha256 "79dddd85d6250421ffb73de8dd59258c611fa928366d90cab563eb0d68cfa0ac"
    end
    on_intel do
      url "https://github.com/bradheitmann/minimux/releases/download/v0.1.1/minimux-v0.1.1-x86_64-linux.tar.gz"
      sha256 "20d47aee1c8ea4e37670da4beed63fe948640b86a892521a74f774fb63d498eb"
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
