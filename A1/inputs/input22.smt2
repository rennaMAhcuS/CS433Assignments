(set-logic AUFLIA)  ; Supports quantifiers and arithmetic

(declare-const p Bool)
(declare-const q Bool)
(declare-const r Bool)

; Universal quantification: ∀x (p ↔ q)
; (assert (forall ((x Bool)) (= p q))) 

; Existential quantification: ∃y (p ↔ r)
; (assert (exists ((y Bool)) (= p r))) 

; Combining universal and existential: ∀x ∃y (x ↔ y)
(assert (forall ((x Bool)) (exists ((y Bool)) (= x y)))) 

(check-sat)
(get-model)
