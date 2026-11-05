from django.conf import settings
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from .analysis import analyze_resume
from .parsing import MAX_RESUME_LENGTH, extract_resume


@never_cache
@require_http_methods(["GET", "POST"])
def index(request):
    context = {
        "api_configured": bool(settings.GEMINI_API_KEY),
        "resume_text": request.POST.get("resume_text", ""),
        "job_description": request.POST.get("job_description", ""),
        "preview": request.POST.get("preview") == "true",
    }
    if request.method == "GET":
        return render(request, "analyzer/index.html", context)

    try:
        action = request.POST.get("action")
        if action == "extract":
            upload = request.FILES.get("resume")
            if not upload:
                raise ValueError("Choose a PDF or DOCX resume first.")
            context["resume_text"] = extract_resume(upload)
            context["preview"] = True
        elif action == "analyze":
            context["preview"] = True
            resume = context["resume_text"].strip()
            job = context["job_description"].strip()
            if not 60 <= len(resume) <= MAX_RESUME_LENGTH:
                raise ValueError("Enter resume text between 60 and 40,000 characters.")
            if not 50 <= len(job) <= 20_000:
                raise ValueError("Enter a job description between 50 and 20,000 characters.")
            context["result"] = analyze_resume(resume, job)
            return render(request, "analyzer/results.html", context)
        elif action == "edit":
            context["preview"] = True
        else:
            raise ValueError("Choose a valid action: upload or analyze your resume.")
    except ValueError as error:
        context["error"] = str(error)
        return render(request, "analyzer/index.html", context, status=400)

    return render(request, "analyzer/index.html", context)
