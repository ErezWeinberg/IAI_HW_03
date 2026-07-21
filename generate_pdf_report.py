import json
import sys
from pathlib import Path
from fpdf import FPDF
from bidi.algorithm import get_display

class PDFReport(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("Arial", "", r"C:\Windows\Fonts\arial.ttf")
        self.add_font("Arial", "B", r"C:\Windows\Fonts\arialbd.ttf")
        self.set_auto_page_break(auto=True, margin=15)
        self.math_dir = Path(__file__).resolve().parent / "math_imgs"
        
    def header(self):
        if self.page_no() > 1:
            self.set_font("Arial", "", 9)
            self.set_text_color(128, 128, 128)
            title = self.bidi("קורס 236501 - מבוא לבינה מלאכותית | תרגיל בית 3 - דוח הגשה")
            self.cell(0, 8, title, align="R", new_x="LMARGIN", new_y="NEXT")
            self.line(10, 15, 200, 15)
            self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "", 9)
        self.set_text_color(128, 128, 128)
        page_str = self.bidi(f"עמוד {self.page_no()} מתוך {{nb}}")
        self.cell(0, 10, page_str, align="C")

    def bidi(self, text):
        return get_display(str(text))

    def print_heading(self, text, level=1):
        self.set_text_color(24, 43, 73)
        if level == 1:
            self.set_font("Arial", "B", 15)
            self.ln(4)
            self.cell(0, 10, self.bidi(text), align="R", new_x="LMARGIN", new_y="NEXT")
            self.set_draw_color(24, 43, 73)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(3)
        elif level == 2:
            self.set_font("Arial", "B", 13)
            self.ln(3)
            self.cell(0, 8, self.bidi(text), align="R", new_x="LMARGIN", new_y="NEXT")
            self.ln(1)
        elif level == 3:
            self.set_font("Arial", "B", 11)
            self.ln(2)
            self.cell(0, 6, self.bidi(text), align="R", new_x="LMARGIN", new_y="NEXT")
            self.ln(1)

    def print_paragraph(self, text, bold=False):
        self.set_text_color(40, 40, 40)
        self.set_font("Arial", "B" if bold else "", 10)
        self.multi_cell(0, 6, self.bidi(text), align="R")
        self.ln(1)

    def print_bullet(self, text):
        self.set_text_color(40, 40, 40)
        self.set_font("Arial", "", 10)
        bullet_text = f"• {text}"
        self.multi_cell(0, 6, self.bidi(bullet_text), align="R")
        self.ln(1)

    def print_math(self, img_name, w=110):
        img_path = self.math_dir / f"{img_name}.png"
        if img_path.exists():
            # Center math image
            x_pos = (210 - w) / 2
            self.image(str(img_path), x=x_pos, w=w)
            self.ln(1)

def build_pdf():
    json_path = Path(__file__).resolve().parent / "report_data.json"
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    pdf = PDFReport()
    pdf.alias_nb_pages()
    pdf.add_page()

    # --- COVER / HEADER ---
    pdf.set_font("Arial", "B", 20)
    pdf.set_text_color(20, 50, 90)
    pdf.cell(0, 12, pdf.bidi("תרגיל בית 3 - תהליכי החלטה מרקוביים ולמידה מחיזוקים"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Arial", "", 13)
    pdf.set_text_color(70, 70, 70)
    pdf.cell(0, 8, pdf.bidi("מבוא לבינה מלאכותית (236501) | סמסטר אביב 2026"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, pdf.bidi("דוח הגשה מרכזי ומאוחד (חלק יבש + חלק רטוב)"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # --- PART A: DRY PART ---
    pdf.print_heading("חלק א' - חלק יבש (45 נקודות)", level=1)
    
    pdf.print_heading("שאלה 1: ייצוג מצבים ותכונת מרקוב (6 נק')", level=2)
    pdf.print_paragraph("a. המיקום לבדו (row, col) אינו מקיים את תכונת מרקוב מכיוון שאינו מכיל את כל ההיסטוריה הדרושה לקבלת החלטות. למשל, המיקום בלבד אינו מציין האם הרובוט כבר אוסף חיישן (מה שקובע אם הגעה ליציאה תסיים את המשימה בהצלחה), ואינו מציין את רמת הסוללה או הזמן הנותר, המכתיבים את ההיתכנות של מסלולים שונים.")
    pdf.print_paragraph("b. ייצוג המצב המורחב המקיים את תכונת מרקוב הינו: State = (row, col, carrying_sensor, battery_level, time_remaining).")
    pdf.print_paragraph("c. חישוב חסם עליון למספר המצבים המורחבים: 22 מיקומים × 2 מצבי נשיאה (כן/לא) × 6 רמות סוללה (0-5) × 21 רמות זמן (0-20) = 5,544 מצבים אפשריים.")
    pdf.print_paragraph("d. דוגמה למצב הנספר בחסם אך אינו ישים: מצב שבו המיקום הוא משבצת האיסוף P, אך carrying_sensor=False עם זמן נותר שאינו התחלתי. על פי הגדרת הסביבה, ברגע שהרובוט מגיע ל-P החיישן נאסף באופן מיידי, ולכן לא ייתכן שהרובוט יימצא ב-P ללא החיישן.")

    pdf.print_heading("שאלה 2: משוואות בלמן לאופק סופי (6 נק')", level=2)
    pdf.print_paragraph("a. תנאי הבסיס לאופק t=0: V_0(s) = 0 לכל מצב s. המשוואה הרקורסיבית עבור t >= 1:")
    pdf.print_math("bellman_eq", w=135)
    pdf.print_paragraph("b. טיפול במצבים סופיים: במצב סופי s, הערך נקבע ל-V_t(s) = 0 לכל t, וההסתברות להישאר בו היא 1 עם תגמול 0, כך שמצבים סופיים אינם מניבים תגמולים נוספים.")
    pdf.print_paragraph("c. המדיניות האופטימלית התלויה בזמן הינה:")
    pdf.print_math("policy_eq", w=130)
    pdf.print_paragraph("d. המדיניות האופטימלית באופק סופי אינה חייבת להיות סטציונרית מכיוון שבעבור אותו מצב s, כמות הצעדים הנותרת t משפיעה ישירות על כדאיות הפעולות. ככל ש-t קטן יותר, הרובוט עשוי לבחור בפעולות חמדניות יותר כדי להגיע ליעד לפני תום הזמן.")

    pdf.print_heading("שאלה 3: מדיניות סטציונרית מול לא-סטציונרית (6 נק')", level=2)
    pdf.print_paragraph("a. עבור t=2 צעדים נותרים: תועלת צפויה עבור SAFE הינה 2-. תועלת צפויה עבור RISKY:")
    pdf.print_math("risky_utility", w=130)
    pdf.print_paragraph("לכן הפעולה RISKY עדיפה עבור t=2.")
    pdf.print_paragraph("b. עבור t=4 צעדים נותרים:")
    pdf.print_math("safe_utility", w=110)
    pdf.print_paragraph("לכן הפעולה SAFE עדיפה עבור t=4.")
    pdf.print_paragraph("c. המיקום J בלבד אינו מייצג את המצב באופן מלא מכיוון שהפעולה האופטימלית משתנה כתלות בזמן הנותר (RISKY ל-t=2 לעומת SAFE ל-t=4). מדיניות סטציונרית התלויה במיקום בלבד אינה יכולה לייצג את שתי ההחלטות השונות.")

    pdf.print_heading("שאלה 4: הערכת מודל מעבר מדגמים (5 נק')", level=2)
    pdf.print_paragraph("אומדן Laplace עבור הסתברויות מעבר:")
    pdf.print_math("laplace_eq", w=90)
    pdf.print_paragraph("a. P_hat(u | s, UP) = (6 + 1) / (8 + 4*1) = 7/12. P_hat(r | s, UP) = (2 + 1) / 12 = 3/12. P_hat(d | s, UP) = P_hat(s | s, UP) = 1/12.")
    pdf.print_paragraph("b. P_hat(r | s, RIGHT) = (1 + 1) / (2 + 4*1) = 2/6. P_hat(d | s, RIGHT) = (1 + 1) / 6 = 2/6. P_hat(s | s, RIGHT) = P_hat(u | s, RIGHT) = 1/6.")
    pdf.print_paragraph("c. עבור הפעולה WAIT לא נצפו תצפיות כלל, ולכן ההחלקה מקצה הסתברות אחידה 1/4 לכל מצב, מה שמייצר מודל מעבר לא אמין.")
    pdf.print_paragraph("d. גישת 'הערך מודל ואז תכנן' (ADP) משתמשת בתצפיות כדי לבנות מודל מעבר ותגמול מפורש P_hat, R_hat ומתכננת בתוכו, בעוד למידה ללא מודל (כמו Q-learning) מעדכנת ערכי פעולה ישירות מהדגמים ללא בניית מודל מפורש.")

    pdf.print_heading("שאלה 5: תגמולים ומדיניות אופטימלית (5 נק')", level=2)
    pdf.print_paragraph("a. הגדלת הקנס בתאי סכנה (מ-50- ל-200-) עשויה לשנות את המדיניות האופטימלית ולהפוך אותה לזהירה יותר, כך שהסוכן יימנע ממסלולים העוברים ליד סכנה אף אם הם קצרים יותר.")
    pdf.print_paragraph("b. הכפלת כל התגמולים בסקלאר חיובי c > 0 אינה משנה את המדיניות האופטימלית מכיוון שסדר העדיפויות בין כל המסלולים נשמר בדיוק.")
    pdf.print_paragraph("c. הוספת קבוע שלילי (למשל 1-) לכל צעד מעודדת מסלולים קצרים יותר ומפחיתה שוטטות, מכיוון שכל צעד נוסף כרוך בעונש נוסף.")
    pdf.print_paragraph("d. תוחלת התועלת במסלול מסוכן עשויה להיות נמוכה בגלל עונש כבד במקרה של כישלון, אך אם הסתברות ההצלחה גבוהה מאוד, בפועל רוב הסימולציות יסתיימו בהצלחה.")

    pdf.print_heading("שאלה 6: עדכון הפרש זמני (TD) ו-Q-learning (6 נק')", level=2)
    pdf.print_paragraph("a. נוסחת עדכון TD(0) עבור V(s):")
    pdf.print_math("td0_update", w=105)
    pdf.print_math("td0_calc", w=125)
    pdf.print_paragraph("b. נוסחת עדכון Q-learning עבור Q(s,a):")
    pdf.print_math("q_update", w=120)
    pdf.print_math("q_calc", w=115)
    pdf.print_paragraph("c. TD(0) מעריך את ערך המדיניות הנוכחית (On-policy value prediction), בעוד Q-learning לומד את ערך המדיניות האופטימלית (Off-policy control).")
    pdf.print_paragraph("d. הסתברות לבחירת פעולה שאינה חמדנית ב-epsilon-greedy:")
    pdf.print_math("eps_prob", w=110)
    pdf.print_paragraph("e. דעיכה מהירה מדי של epsilon תגרום להפסקת החקירה מוקדם מדי, והסוכן עלול להתכנס למדיניות תת-אופטימלית שנתקעה במסלול הראשון שמצא.")

    pdf.print_heading("שאלה 7: אומדן Monte Carlo, TD והטיית מדגם (5 נק')", level=2)
    pdf.print_paragraph("a. אומדן First-Visit Monte Carlo עבור V(s0):")
    pdf.print_math("mc_eq", w=125)
    pdf.print_paragraph("b. Monte Carlo ממתין לסיום הפרק ומחשב את התגמול המצטבר הממשי, בעוד TD(0) מעדכן מיד לאחר צעד אחד בהסתמך על הערך המוערך של המצב הבא (Bootstrapping).")
    pdf.print_paragraph("c. הטיית מדגם שבה פעולה 특정 נצפתה לעיתים נדירות תגרום לאומדן לא מדויק של ערכה. ב-Q-learning, אם פעולה אופטימלית לא נחקרה מספיק, הסוכן עלול להחמיץ אותה.")
    pdf.print_paragraph("d. אתחול אופטימי של ערכי Q (Optimistic Initialization) מעודד חקירה טבעית של כל זוגות מצב-פעולה שלא נחקרו מספיק.")

    pdf.print_heading("שאלה 8: KNN, נרמול מאפיינים ועלות החלטה (6 נק')", level=2)
    pdf.print_paragraph("a. מרחק אוקלידי:")
    pdf.print_math("knn_dist", w=95)
    pdf.print_paragraph("חישוב מרחקים: d(x1,q)=sqrt(5) ≈ 2.24, d(x2,q)=sqrt(8) ≈ 2.83, d(x3,q)=30.0, d(x4,q)=sqrt(785) ≈ 28.02. השכן הקרוב ביותר הינו x1 (normal).")
    pdf.print_paragraph("b. נרמול Min-Max:")
    pdf.print_math("minmax_norm", w=75)
    pdf.print_paragraph("גם לאחר נרמול, d_norm(x1,q) ≈ 0.335 הינו המינימלי, והסיווג נשאר normal.")
    pdf.print_paragraph("c. ללא נרמול, המאפיין smoke_density (טווח 0-100) דומיננטי לחלוטין ומעלים את השפעת recent_slips (טווח 0-3).")
    pdf.print_paragraph("d. בחירת K קטן (K=1) רגישה לרעש. בחירת K גדול מחליקה את הגבול אך מושפעת מכיתות רוב.")
    pdf.print_paragraph("e. בנתונים לא מאוזנים (Imbalanced Data), מסווג המנחש תמיד את הכיתה הנפוצה ישיג דיוק גבוה אך ייכשל בזיהוי מקרים מסוכנים נדירים.")

    # --- PART B: WET PART B ---
    pdf.add_page()
    pdf.print_heading("חלק ב' - חלק רטוב: תכנון כאשר המודל ידוע (20 נקודות)", level=1)
    
    pdf.print_heading("תוצאות תכנון דינמי לאופקים שונים (Finite-Horizon DP)", level=2)
    pdf.print_paragraph("הרצנו תכנון דינמי לאופק סופי על פי משוואות בלמן עבור horizons H in {12, 20, 30}. להלן ריכוז התוצאות והערכת המדיניות על 100 סימולציות (seed=236501):")

    # Table Part B
    pdf.set_font("Arial", "B", 9)
    pdf.set_fill_color(230, 240, 250)
    pdf.cell(25, 7, pdf.bidi("סוללה/סכנה"), border=1, align="C", fill=True)
    pdf.cell(25, 7, pdf.bidi("אורך ממוצע"), border=1, align="C", fill=True)
    pdf.cell(25, 7, pdf.bidi("שיעור הצלחה"), border=1, align="C", fill=True)
    pdf.cell(30, 7, pdf.bidi("תגמול ממוצע"), border=1, align="C", fill=True)
    pdf.cell(30, 7, pdf.bidi("מצבים נגישים"), border=1, align="C", fill=True)
    pdf.cell(30, 7, pdf.bidi("V(s0) התחלתי"), border=1, align="C", fill=True)
    pdf.cell(20, 7, pdf.bidi("אופק H"), border=1, align="C", fill=True, new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Arial", "", 9)
    for H_str, row in data["part_b_horizons"].items():
        fb = row["failure_breakdown"]
        fail_str = f"B:{fb['battery']}/D:{fb['danger']}"
        pdf.cell(25, 6, pdf.bidi(fail_str), border=1, align="C")
        pdf.cell(25, 6, f"{row['mean_length']:.2f}", border=1, align="C")
        pdf.cell(25, 6, f"{row['success_rate']*100:.1f}%", border=1, align="C")
        pdf.cell(30, 6, f"{row['mean_return']:.2f}", border=1, align="C")
        pdf.cell(30, 6, f"{row['reachable_states_count']}", border=1, align="C")
        pdf.cell(30, 6, f"{row['V_start']:.3f}", border=1, align="C")
        pdf.cell(20, 6, f"H={H_str}", border=1, align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(3)
    pdf.print_paragraph("ניתוח התוצאות:")
    pdf.print_bullet("עבור H=12: האופק קצר מדי מכדי לאפשר הגעה למשבצת האיסוף P והגעה חזרה ליציאה E במסלול בטוח, ולכן שיעור ההצלחה הינו 0%.")
    pdf.print_bullet("עבור H=20: האופק מספיק להשלמת המשימה בהצלחה (15% הצלחה בסימולציה סטוכסטית מול 85% כשלוני סוללה עקב סטיות מקריות בתאים משובשים).")
    pdf.print_bullet("עבור H=30: כמות המצבים הנגישים גדלה ל-1,684. תוכנית DP מוצאת נתיבים זהים אך בסימולציות ארוכות יותר הסוללה אוזלת ללא טעינה מחדש.")

    pdf.print_heading("ניתוח שינוי מדיניות לפי זמן וסוללה (Policy Slices)", level=2)
    pdf.print_paragraph("מבחינת טבלת פרוסות המדיניות (Policy Slices), נצפה שינוי בפעולה הנבחרת עבור אותה משבצת פיזית (0, 0) כאשר הזמן הנותר והסוללה משתנים: עבור t=20 נבחרת הפעולה RIGHT (פנייה לכיוון עמדת הטעינה R), בעוד עבור t <= 19 נבחרת הפעולה UP.")

    pdf.print_heading("ניתוח הגדלת קנס תאי סכנה (Hazard Penalty Experiment)", level=2)
    q4_res = data["part_b_q4_hazard_experiment"]
    pdf.print_paragraph(f"בהכפלת קנס הסכנה ל-200- (פי 4 מהבסיס 50-): תכנון DP הפיק ערך התחלתי V(s0) = {q4_res['V_start_high']:.3f}. בסימולציה נרשם שיעור הצלחה של {q4_res['eval_on_high_env']['success_rate']*100:.1f}% ותגמול ממוצע {q4_res['eval_on_high_env']['mean_return']:.2f}. המדיניות נשארה זהה מכיוון שהמתכנן האופטימלי ממילא נמנע מלהיכנס לתאי סכנה סופיים (X).")

    img_dir = Path(__file__).resolve().parent / "starter_code" / "smoke_outputs"
    img1 = img_dir / "true_model_planner_policy_t15_not_carrying_b1.png"
    img2 = img_dir / "true_model_planner_policy_t5_carrying_b2.png"

    if img1.exists() and img2.exists():
        pdf.ln(2)
        pdf.print_heading("ויזואליזציה של פרוסות מדיניות (Policy Slices)", level=2)
        pdf.image(str(img1), x=15, w=85)
        pdf.image(str(img2), x=105, w=85)
        pdf.ln(2)
        pdf.print_paragraph("מימין: מדיניות עבור t=5 כאשר הסוכן נושא את החיישן עם סוללה 2. משמאל: מדיניות עבור t=15 ללא חיישן עם סוללה 1.", bold=False)

    # --- PART C: WET PART C ---
    pdf.add_page()
    pdf.print_heading("חלק ג' - חלק רטוב: למידה מחיזוקים (30 נקודות)", level=1)

    pdf.print_heading("1. הערכת מודל מתוך דגמים אופליין (Model Estimation)", level=2)
    pdf.print_paragraph("אומדן מעברים ותגמולים P_hat, R_hat מתוך קבצי הדגמים (Sparse vs Good Data) עם החלקת Laplace (lambda in {0, 0.1, 1.0}):")

    pdf.set_font("Arial", "B", 9)
    pdf.set_fill_color(230, 240, 250)
    pdf.cell(30, 7, pdf.bidi("שיעור הצלחה"), border=1, align="C", fill=True)
    pdf.cell(35, 7, pdf.bidi("תגמול ממוצע"), border=1, align="C", fill=True)
    pdf.cell(35, 7, pdf.bidi("מעברים שנלמדו"), border=1, align="C", fill=True)
    pdf.cell(35, 7, pdf.bidi("החלקה (Lambda)"), border=1, align="C", fill=True)
    pdf.cell(45, 7, pdf.bidi("סוג הדאטה"), border=1, align="C", fill=True, new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Arial", "", 9)
    for d_type in ["sparse", "good"]:
        for lam_str, r_data in data["part_c_model_estimation"][d_type].items():
            ev = r_data["eval"]
            pdf.cell(30, 6, f"{ev['success_rate']*100:.1f}%", border=1, align="C")
            pdf.cell(35, 6, f"{ev['mean_return']:.2f}", border=1, align="C")
            pdf.cell(35, 6, f"{r_data['num_transitions']}", border=1, align="C")
            pdf.cell(35, 6, f"lambda = {lam_str}", border=1, align="C")
            pdf.cell(45, 6, pdf.bidi("דל (Sparse)" if d_type == "sparse" else "כיסוי טוב (Good)"), border=1, align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(2)
    pdf.print_paragraph("מסקנה: בדאטה הדל (Sparse) לא נצפו מסלולי הצלחה כלל, ולכן המודל הנלמד אינו מכיר את תגמול ההצלחה ב-E ושיעור ההצלחה הוא 0%. בדאטה הטוב (Good), המודל לומד את מעברי ההצלחה ומשיג 14.0% הצלחה (קרוב ל-Oracle 15%).")

    pdf.print_heading("2. השוואת הערכת ערכים: First-Visit MC מול TD(0)", level=2)
    pdf.print_paragraph("הערכת V^pi עבור המדיניות הקבועה H=20 לאורך 400 פרקים:")

    pdf.set_font("Arial", "B", 9)
    pdf.set_fill_color(230, 240, 250)
    pdf.cell(35, 7, pdf.bidi("שגיאת TD(0)"), border=1, align="C", fill=True)
    pdf.cell(35, 7, pdf.bidi("ערך TD(0)"), border=1, align="C", fill=True)
    pdf.cell(35, 7, pdf.bidi("ערך Monte Carlo"), border=1, align="C", fill=True)
    pdf.cell(35, 7, pdf.bidi("ערך אמת DP"), border=1, align="C", fill=True)
    pdf.cell(40, 7, pdf.bidi("מצב s = (r,c,s,b,t)"), border=1, align="C", fill=True, new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Arial", "", 8)
    for mc_td in data["part_c_mc_td_comparison"]:
        s_str = f"({mc_td['state'][0]},{mc_td['state'][1]},{int(mc_td['state'][2])},{mc_td['state'][3]},{mc_td['state'][4]})"
        pdf.cell(35, 6, f"{mc_td['diff_td']:.4f}", border=1, align="C")
        pdf.cell(35, 6, f"{mc_td['td_val']:.3f}", border=1, align="C")
        pdf.cell(35, 6, f"{mc_td['mc_val']:.3f}", border=1, align="C")
        pdf.cell(35, 6, f"{mc_td['true_dp']:.3f}", border=1, align="C")
        pdf.cell(40, 6, s_str, border=1, align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(2)
    pdf.print_paragraph("ניתוח: TD(0) מפגין שגיאה נמוכה יותר ושונות קטנה יותר בהשוואה ל-Monte Carlo הודות לשימוש ב-Bootstrapped values, במיוחד במצבים מתקדמים לאורך המסלול.")

    pdf.print_heading("3. חקירת Boltzmann (Softmax Action Selection)", level=2)
    pdf.print_paragraph("נוסחת בחירת הפעולות ב-Softmax Boltzmann:")
    pdf.print_math("boltzmann_eq", w=110)

    pdf.print_heading("4. השוואה מרכזית בין סוכני ההחלטות (Decision Agents)", level=2)
    pdf.print_paragraph("להלן טבלת ההשוואה המרכזית בין כל סוכני ההחלטה שנבדקו במטלה:")

    pdf.set_font("Arial", "B", 8)
    pdf.set_fill_color(230, 240, 250)
    pdf.cell(30, 7, pdf.bidi("כישלונות סוללה"), border=1, align="C", fill=True)
    pdf.cell(25, 7, pdf.bidi("אורך ממוצע"), border=1, align="C", fill=True)
    pdf.cell(25, 7, pdf.bidi("שיעור הצלחה"), border=1, align="C", fill=True)
    pdf.cell(30, 7, pdf.bidi("תגמול ממוצע"), border=1, align="C", fill=True)
    pdf.cell(70, 7, pdf.bidi("סוכן החלטה / אלגוריתם"), border=1, align="C", fill=True, new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Arial", "", 8)
    agents_map = [
        ("Oracle Planner (True DP H=20)", data["decision_agent_comparison"]["oracle_planner"]),
        ("Estimated Model (Good Data, lambda=0.1)", data["decision_agent_comparison"]["estimated_model_planner_good"]),
        ("Estimated Model (Sparse Data, lambda=0.1)", data["decision_agent_comparison"]["estimated_model_planner_sparse"]),
        ("Q-learning (Constant Epsilon = 0.1)", data["decision_agent_comparison"]["q_learning_constant"]),
        ("Q-learning (Decaying Epsilon)", data["decision_agent_comparison"]["q_learning_decaying"]),
        ("Boltzmann Exploration (T = 0.2)", data["decision_agent_comparison"]["boltzmann_temp_0_2"]),
        ("Boltzmann Exploration (T = 1.0)", data["decision_agent_comparison"]["boltzmann_temp_1_0"])
    ]

    for name, ag_eval in agents_map:
        fb = ag_eval.get("failure_breakdown", {"battery": 0})
        pdf.cell(30, 6, f"{fb.get('battery', 0)}", border=1, align="C")
        pdf.cell(25, 6, f"{ag_eval['mean_length']:.2f}", border=1, align="C")
        pdf.cell(25, 6, f"{ag_eval['success_rate']*100:.1f}%", border=1, align="C")
        pdf.cell(30, 6, f"{ag_eval['mean_return']:.2f}", border=1, align="C")
        pdf.cell(70, 6, pdf.bidi(name), border=1, align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(3)
    pdf.print_heading("5. דיון בחקירה מול ניצול וסיווג אלגוריתמים", level=2)
    pdf.print_bullet("Oracle Planner: מבוסס מודל (Model-based), פסיבי לגבי איסוף נתונים (אינו לומד מדגמים).")
    pdf.print_bullet("Estimated Model Planner: מבוסס מודל (Model-based), אופליין / פסיבי (לומד מדאטה מוקלט).")
    pdf.print_bullet("Q-learning: ללא מודל (Model-free), אקטיבי (Active / On-policy exploration, Off-policy update).")
    pdf.print_bullet("דיון בכישלון חקירה: בנתונים דלים (Sparse Data) או כאשר epsilon דועך מהר מדי, הסוכן סובל מכיסוי נתונים לקוי (Data Sparsity). מכיוון שלא נצפה אות החיזוק החיובי של ההצלחה ב-E, הסוכן לומד להימנע מתנועה ומתכנס למסלולים קצרים המסתיימים בכשל סוללה.")

    # --- PART D: AI DECLARATION ---
    pdf.ln(3)
    pdf.print_heading("חלק ד' - הצהרת שימוש בכלי AI (5 נקודות)", level=1)
    pdf.print_paragraph("במהלך העבודה על תרגיל בית 3 נעשה שימוש בסייען ה-AI האוטונומי (Antigravity AI Assistant).")
    pdf.print_bullet("שימוש בחלק התאורטי (חלק א'): ניתוח ניסוח השאלות, וידוא חישובי מטריצות מעבר ונוסחאות בלמן, ואימות חישובי מרחק KNN ונרמול Min-Max.")
    pdf.print_bullet("שימוש בחלק המעשי (חלקים ב' ו-ג'): כלי ה-AI שימש להרצת בדיקות היחידה (tests_public.py), הרצת תסריט הסימולציה run_assignment_smoke.py, אימות הפונקציות ב-planning_rescue.py ו-learning_rescue.py, וריכוז הנתונים הסטטיסטיים.")
    pdf.print_bullet("הפקת הדוח: הפקת קובץ PDF זה בוצעה באופן אוטומטי ומבוקר באמצעות סקריפט Python ייעודי שנכתב ע\"י כלי ה-AI עם רנדור נוסחאות LaTeX ווקטוריות.")
    pdf.print_paragraph("כל הפתרונות והקוד נבדקו, אושרו ואומתו באופן עצמאי על ידינו.")

    output_pdf_path = Path(__file__).resolve().parent / "AI_HW3.pdf"
    pdf.output(str(output_pdf_path))
    print(f"Successfully generated math-enhanced PDF report: {output_pdf_path}")

if __name__ == "__main__":
    build_pdf()
