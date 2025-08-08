SELECT
		 "連絡先"."取引先名",
		 "連絡先"."氏名",
		 "Answer"."Category",
		 "Answer"."Created at",
		 "Answer"."eMail",
		 "Answer"."Feedback_IsCorrect",
		 "Answer"."Feedback_Text",
		 "Answer"."Question_Text",
		 "Answer"."Question_Audio",
		 "Answer"."Question_Japanese",
		 "Answer"."User_Text",
		 "Answer"."User_Audio",
		 "Answer"."OverAll",
		 "Answer"."Pronounciation",
		 "Answer"."Vocabulary",
		 "Answer"."Fluency",
		 "Answer"."Sentence Mastery"
FROM  "Answer"
JOIN "連絡先" ON "Answer"."eMail"  = "連絡先"."メール"  
WHERE	 "Answer"."eMail"  <> 'admin@cts-n.net'
