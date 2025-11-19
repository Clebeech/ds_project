-- 创建触发器：当插入访谈记录时，自动更新调研员的完成次数
DROP TRIGGER IF EXISTS trg_update_interview_count;

DELIMITER //
CREATE TRIGGER trg_update_interview_count
AFTER INSERT ON interviews
FOR EACH ROW
BEGIN
    UPDATE surveyors 
    SET CompletedInterviews = COALESCE(CompletedInterviews, 0) + 1
    WHERE SurveyorID = NEW.SurveyorID;
END;//
DELIMITER ;

