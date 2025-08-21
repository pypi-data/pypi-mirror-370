class Trmd < Formula
  include Language::Python::Virtualenv

  desc "Translate Markdown using OpenAI"
  homepage "https://github.com/rioriost/homebrew-trmd/"
  url "https://files.pythonhosted.org/packages/0b/39/a313063d251a2efa32a4b44592cd0fcf3d627d9e40ae36001aeedd63b0f7/trmd-0.1.16.tar.gz"
  sha256 "dedb626c5f41e8b3481786917ef32eb52890e80803e48c6647dd7136fdddc269"
  license "MIT"

  depends_on "python@3.13"

  def install
    virtualenv_install_with_resources
    system libexec/"bin/python", "-m", "pip", "install", "openai"
  end

  test do
    system "#{bin}/trmd", "--help"
  end
end
