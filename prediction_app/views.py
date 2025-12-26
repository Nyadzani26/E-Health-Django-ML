from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect, FileResponse
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import DiabetesPrediction, ModelRegistry, DriftLog
import pandas as pd

import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter


def index(request):
    return render(request, "index.html")


@login_required
def diabetes_prediction(request):
    if request.method == "POST":

        age = float(request.POST.get("age"))
        sex = float(request.POST.get("sex"))
        bmi = float(request.POST.get("bmi"))
        bp = float(request.POST.get("bp"))
        tc = float(request.POST.get("tc"))
        ldl = float(request.POST.get("ldl"))
        hdl = float(request.POST.get("hdl"))
        tch = float(request.POST.get("tch"))
        ltg = float(request.POST.get("ltg"))
        glucose = float(request.POST.get("glucose"))
        user = request.user

        diabetes_model = pd.read_pickle("data_model/model.pickle")
        features = [[age, sex, bmi, bp, tc, ldl, hdl, tch, ltg, glucose]]
        try:
            # Try probability if available
            proba = None
            if hasattr(diabetes_model, "predict_proba"):
                proba = float(diabetes_model.predict_proba(features)[0][1])
            pred = diabetes_model.predict(features)
            pred_val = float(pred[0]) if hasattr(pred, "__iter__") else float(pred)
        except Exception:
            proba = None
            pred_val = 0.0

        # Map to label (fallback threshold if model outputs a score)
        if proba is not None:
            label = "Diabetic" if proba >= 0.5 else "No Diabetes"
        else:
            label = "Diabetic" if pred_val >= 0.75 else "No Diabetes"

        # Capture a simple model version tag
        model_version = getattr(diabetes_model, '__class__', type(diabetes_model)).__name__ or 'v1'
        # Attempt SHAP explanations (optional dependency)
        top_factors_json = ""
        try:
            import json
            import numpy as np
            try:
                import shap  # type: ignore
                explainer = shap.Explainer(diabetes_model)
                shap_values = explainer(np.array(features))
                # shap_values may be a Explanation object
                vals = getattr(shap_values, 'values', None)
                if vals is None:
                    vals = shap_values  # best effort
                vals = np.array(vals)[0].tolist()
                feature_names = ["age","sex","bmi","bp","tc","ldl","hdl","tch","ltg","glucose"]
                pairs = []
                for i, v in enumerate(vals):
                    pairs.append({"feature": feature_names[i], "value": float(features[0][i]), "impact": float(v), "direction": "+" if v>=0 else "-"})
                pairs = sorted(pairs, key=lambda x: abs(x["impact"]), reverse=True)[:3]
                top_factors_json = json.dumps(pairs)
            except Exception:
                # Fallback using feature_importances_ if available
                import numpy as np
                fi = getattr(diabetes_model, 'feature_importances_', None)
                feature_names = ["age","sex","bmi","bp","tc","ldl","hdl","tch","ltg","glucose"]
                if fi is not None:
                    fi = (fi / (np.sum(fi) or 1.0)).tolist()
                    pairs = []
                    for i, w in enumerate(fi):
                        pairs.append({"feature": feature_names[i], "value": float(features[0][i]), "impact": float(w), "direction": "+" if (proba or pred_val)>=0.5 else "-"})
                    pairs = sorted(pairs, key=lambda x: abs(x["impact"]), reverse=True)[:3]
                    top_factors_json = json.dumps(pairs)
        except Exception:
            top_factors_json = ""

        prediction = DiabetesPrediction(
            age=age,
            sex=sex,
            bmi=bmi,
            bp=bp,
            tc=tc,
            ldl=ldl,
            hdl=hdl,
            tch=tch,
            ltg=ltg,
            glucose=glucose,
            result=label,
            model_version=model_version,
            probability= float(proba) if proba is not None else float(pred_val),
            top_factors= top_factors_json,
            user=user)
        prediction.save()

        # Drift logging (basic): compare inputs to last registry record means if available
        try:
            import json, numpy as np
            latest_registry = ModelRegistry.objects.order_by('-trained_at').first()
            summary = {}
            feature_names = ["age","sex","bmi","bp","tc","ldl","hdl","tch","ltg","glucose"]
            vals = features[0]
            if latest_registry and latest_registry.feature_names:
                # Placeholder: store raw values; in a real setup include training means/vars
                for i, f in enumerate(feature_names):
                    summary[f] = {"value": float(vals[i])}
            DriftLog.objects.create(user=user, model_version=model_version, summary=json.dumps(summary))
        except Exception:
            pass

        return HttpResponseRedirect(reverse("diabetes_result"))

    return render(request, "prediction/diabetes.html")


@login_required
def diabetes_result(request):
    latest = (
        DiabetesPrediction.objects
        .filter(user=request.user)
        .order_by("-created_at")
        .first()
    )
    return render(request, "prediction/result.html", {"latest": latest})


@login_required
def doctor_dashboard(request):
    if not request.user.role == 'doctor' and not request.user.is_staff:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("You do not have permission to view this page.")
    
    # Get all patients and their latest predictions
    from account.models import Patient
    patients = Patient.patient.all()
    
    context = {
        'patients': patients,
    }
    return render(request, "doctor_dashboard.html", context)


@login_required
def download(request):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)

    prediction = DiabetesPrediction.objects.all()
    user = request.user
    prediction = prediction.filter(user=user)

    lines = []

    for predict in prediction:
        lines.append("age " + str(predict.age))
        lines.append("sex " + str(predict.sex))
        lines.append("bmi " + str(predict.bmi))
        lines.append("bp " + str(predict.bp))
        lines.append("tc " + str(predict.tc))
        lines.append("ldl " + str(predict.ldl))
        lines.append("hdl " + str(predict.hdl))
        lines.append("tch " + str(predict.tch))
        lines.append("ltg " + str(predict.ltg))
        lines.append("glucose " + str(predict.glucose))
        lines.append("date " + str(predict.created_at))
        lines.append("result " + str(predict.result))

        lines.append(" ")
        lines.append(" ")

    for line in lines:
        textob.textLine(line)

    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)

    return FileResponse(buf, as_attachment=True, filename='diabetesresult.pdf')


def about(request):
    return render(request, "about.html")


def contact(request):
    return render(request, "contact.html")


@login_required
def history(request):
    qs = (
        DiabetesPrediction.objects
        .filter(user=request.user)
        .order_by('-created_at')
    )
    return render(request, "prediction/history.html", {"items": qs})


@login_required
def monitor(request):
    if not request.user.is_staff:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden()
    models = ModelRegistry.objects.order_by('-trained_at')[:10]
    logs = DriftLog.objects.order_by('-created_at')[:50]
    return render(request, "prediction/monitor.html", {"models": models, "logs": logs})


@login_required
def export_csv(request):
    import csv
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="wellsight_predictions.csv"'
    writer = csv.writer(response)
    writer.writerow(['date', 'age', 'sex', 'bmi', 'bp', 'tc', 'ldl', 'hdl', 'tch', 'ltg', 'glucose', 'result'])
    for p in DiabetesPrediction.objects.filter(user=request.user).order_by('-created_at'):
        writer.writerow([p.created_at, p.age, p.sex, p.bmi, p.bp, p.tc, p.ldl, p.hdl, p.tch, p.ltg, p.glucose, p.result])
    return response
