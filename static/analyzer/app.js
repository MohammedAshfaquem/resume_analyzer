const resumeText = document.querySelector('#resume-text');
const jobText = document.querySelector('#job-description');
const fileInput = document.querySelector('#resume-file');

function updateCount(field) {
    const counter = document.querySelector(`[data-count-for="${field.id}"]`);
    if (counter) counter.textContent = `${field.value.length.toLocaleString()} / ${field.maxLength.toLocaleString()}`;
}

document.querySelectorAll('textarea[maxlength]').forEach((field) => {
    updateCount(field);
    field.addEventListener('input', () => updateCount(field));
});

fileInput?.addEventListener('change', () => {
    document.querySelector('#file-label').textContent = fileInput.files[0]?.name || 'Choose your resume';
});

document.querySelector('#load-example')?.addEventListener('click', () => {
    if ((resumeText.value.trim() || jobText.value.trim()) && !window.confirm('Replace the current text with an example?')) return;
    resumeText.value = `Alex Morgan — Junior Python Developer
Skills: Python, Django, SQL, Git, HTML, CSS
Project: Campus Events
Built Django APIs with Python for a student event platform. Designed relational data models and used PostgreSQL. Wrote automated tests for event creation and registration. Used Git to collaborate with two classmates.
Education: BSc Computer Science
Looking for an entry-level backend development role.`;
    jobText.value = `Junior Backend Developer
We are looking for a junior developer to build and maintain web APIs.
Required qualifications:
- Python and Django development experience.
- Experience designing relational databases using PostgreSQL.
- Ability to write automated tests and use Git.
- Familiarity with Docker and deploying web applications.
Preferred qualifications:
- Experience with CI/CD pipelines.
Responsibilities: build reliable REST APIs and collaborate on backend features.`;
    updateCount(resumeText);
    updateCount(jobText);
    document.querySelector('#example-message').hidden = false;
    resumeText.focus();
});

let submitting = false;
document.querySelector('[data-loading-form]')?.addEventListener('submit', (event) => {
    if (submitting) {
        event.preventDefault();
        return;
    }
    const action = event.submitter?.value;
    if (action === 'extract' && !fileInput.files.length) {
        event.preventDefault();
        fileInput.focus();
        return;
    }
    submitting = true;
    if (action === 'analyze') {
        document.querySelector('#loading-message').hidden = false;
        document.querySelector('#loading-message').scrollIntoView({ behavior: reducedMotion.matches ? 'auto' : 'smooth', block: 'nearest' });
    }
    // Keep submit buttons enabled so their action value is included in the POST.
    document.querySelectorAll('button[type="submit"]').forEach((button) => button.setAttribute('aria-disabled', 'true'));
    event.currentTarget.setAttribute('aria-busy', 'true');
});

window.addEventListener('pageshow', () => {
    submitting = false;
    document.querySelector('[aria-busy]')?.removeAttribute('aria-busy');
    document.querySelectorAll('button[aria-disabled]').forEach((button) => button.removeAttribute('aria-disabled'));
    const loading = document.querySelector('#loading-message');
    if (loading) loading.hidden = true;
});

function downloadReport() {
    const report = JSON.parse(document.querySelector('#report-data').textContent);
    const lines = [
        `ROLEWISE — ${report.role}`,
        `Requirement coverage: ${report.score}%`,
        'AI guidance, not an ATS score or hiring prediction.',
        '', report.summary, '', 'REQUIREMENT BREAKDOWN',
    ];
    report.requirements.forEach((item) => {
        const status = item.status === 'missing' ? 'not demonstrated' : item.status;
        lines.push('', `${item.requirement} (${item.importance}): ${status}`, item.explanation,
            `Job evidence: ${item.job_evidence}`, `Resume evidence: ${item.resume_evidence || 'No verified supporting excerpt.'}`,
            `Next step: ${item.action}`);
    });
    lines.push('', 'IMPROVEMENTS', ...report.improvements.map((item, index) => `${index + 1}. ${item}`));
    lines.push('', 'WORDING DRAFTS — verify all claims before use');
    report.rewrites.forEach((item) => lines.push('', `Original: ${item.original}`, `Suggested: ${item.suggested}`));
    lines.push('', 'SCORING', 'Required weight: 2; preferred weight: 1. Supported: full credit; partial: half credit; missing or unclear: zero. Coverage = earned / possible × 100. AI interpretation may be incomplete or mistaken.');
    const url = URL.createObjectURL(new Blob([lines.join('\n')], { type: 'text/plain;charset=utf-8' }));
    const link = document.createElement('a');
    link.href = url;
    link.download = 'rolewise-fit-report.txt';
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
}

document.querySelector('#download-report')?.addEventListener('click', downloadReport);

// Motion is optional: the complete page and final score work without JavaScript.
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

function animateScore() {
    const score = document.querySelector('[data-score]');
    if (!score || reducedMotion.matches) return;
    const target = Number(score.dataset.score);
    const start = performance.now();

    function tick(now) {
        const progress = Math.min((now - start) / 1200, 1);
        const eased = 1 - (1 - progress) ** 3;
        score.textContent = `${Math.round(target * eased)}%`;
        if (progress < 1 && !reducedMotion.matches) requestAnimationFrame(tick);
        else score.textContent = `${target}%`;
    }
    requestAnimationFrame(tick);
}

function revealCards() {
    if (reducedMotion.matches || !('IntersectionObserver' in window)) return;
    document.documentElement.classList.add('motion-enabled');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
        });
    }, { threshold: 0.05 });
    document.querySelectorAll('.panel, .stat, .principles > div').forEach((card) => {
        card.classList.add('reveal');
        observer.observe(card);
    });
}

animateScore();
revealCards();
