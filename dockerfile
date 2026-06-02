FROM python:3.12-slim

WORKDIR /app

# Base system packages — update + install + clean in one layer so apt cache is never committed
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-jdk-headless git curl unzip xz-utils ca-certificates \
    apt-transport-https golang rubygems maven bash wget gnupg php \
    && rm -rf /var/lib/apt/lists/*

# .NET SDK — requires Microsoft's package source, so a second apt cycle is unavoidable
RUN wget -q https://packages.microsoft.com/config/debian/13/packages-microsoft-prod.deb -O packages-microsoft-prod.deb \
    && dpkg -i packages-microsoft-prod.deb \
    && rm packages-microsoft-prod.deb \
    && apt-get update \
    && apt-get install -y --no-install-recommends dotnet-sdk-10.0 dotnet-runtime-10.0 dotnet-runtime-9.0 \
    && rm -rf /var/lib/apt/lists/*

# Trivy + cppcheck — trivy requires its own Aquasecurity apt source
RUN wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | gpg --dearmor | tee /usr/share/keyrings/trivy.gpg > /dev/null \
    && echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb generic main" | tee /etc/apt/sources.list.d/trivy.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends trivy cppcheck \
    && rm -rf /var/lib/apt/lists/* \
    && command -v trivy && command -v cppcheck

# Composer
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer \
    && command -v composer

# Python security tools — single pip call, no cache written to image
# setuptools<81 is pinned because semgrep's opentelemetry dep still imports pkg_resources
RUN pip install --no-cache-dir --break-system-packages \
    "setuptools<81" semgrep bandit flawfinder njsscan \
    && command -v semgrep && command -v bandit && command -v flawfinder && command -v njsscan

# Go security tools — purge build + module caches after install to reclaim ~500 MB
RUN GOBIN=/usr/local/bin go install github.com/boyter/scc/v3@latest \
    && GOBIN=/usr/local/bin go install github.com/securego/gosec/v2/cmd/gosec@latest \
    && go clean -cache -modcache \
    && command -v scc && command -v gosec

# Bearer CLI
RUN curl -sfL https://raw.githubusercontent.com/Bearer/bearer/main/contrib/install.sh | sh -s -- -b /usr/local/bin \
    && command -v bearer

# Brakeman (Ruby gem) — --no-document skips ri/rdoc, gem cleanup removes build artefacts
RUN gem install brakeman --no-document \
    && gem cleanup \
    && command -v brakeman

# SpotBugs — ENV must precede the RUN so PATH is visible for the inline verification
ENV SPOTBUGS_HOME=/usr/local/spotbugs-4.9.8
ENV PATH="$SPOTBUGS_HOME/bin:$PATH"
RUN curl -L -o /tmp/spotbugs.tgz https://github.com/spotbugs/spotbugs/releases/download/4.9.8/spotbugs-4.9.8.tgz \
    && tar -xzf /tmp/spotbugs.tgz -C /usr/local \
    && rm /tmp/spotbugs.tgz \
    && command -v spotbugs

# DevSkim (.NET global tool)
ENV PATH="$PATH:/root/.dotnet/tools"
RUN dotnet tool install --global Microsoft.CST.DevSkim.CLI \
    && command -v devskim

# PHPStan via Composer — PATH set first so the inline check resolves the binary
ENV PATH="/opt/phpstan/vendor/bin:${PATH}"
RUN mkdir -p /opt/phpstan \
    && cd /opt/phpstan \
    && composer require --dev phpstan/phpstan \
    && composer clear-cache \
    && command -v phpstan

# OpenGrep — clean up the download directory after extracting the binary
RUN curl -fsSL https://raw.githubusercontent.com/opengrep/opengrep/main/install.sh | bash \
    && install -m 0755 /root/.opengrep/cli/latest/opengrep /usr/local/bin/opengrep \
    && rm -rf /root/.opengrep \
    && command -v opengrep

# CodeQL
RUN mkdir -p /opt/codeql \
    && wget -qO- https://github.com/github/codeql-action/releases/download/codeql-bundle-v2.25.5/codeql-bundle-linux64.tar.gz | tar xz -C /opt/codeql --strip-components=1 \
    && ln -sf /opt/codeql/codeql /usr/local/bin/codeql \
    && command -v codeql

COPY . .

RUN pip install --no-cache-dir .

ENTRYPOINT ["python", "src/main.py"]
