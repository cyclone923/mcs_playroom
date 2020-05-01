;; Specification in PDDL1 of the Question domain

(define (domain playroom)
 (:requirements
    :adl
 )
 (:types
  agent
  location
  object
 )

 (:predicates
    (agentAtLocation ?a - agent ?l - location)                ; true if the agent is at the location
    (objectAtLocation ?o - object ?l - location)              ; true if the object is at the location

    (handEmpty ?a - agent)                                    ; agent ?a not holding anything
    (held ?a - agent ?o - object)                             ; agent ?a is holding object ?o
    (headTiltZero ?a - agent)                                 ; agent ?a is looking straightly to front
    (lookingAtObject ?a - agent ?o - object)                  ; agent ?a is looking at object ?o
    (inReceptacle ?o1 - object ?o2 - object)                  ; object ?o1 is in receptacle ?o2
    (openable ?o)                                             ; true if ?o can be opened
    (isOpened ?o)                                             ; true if ?o is opened
 )

 (:functions
    (totalCost)
 )

;; All actions are specified such that the final arguments are the ones used
;; for performing actions in Unity.

 (:action FaceToFront
    :parameters (?a - agent)
    :effect (and
                (headTiltZero ?a)
                (forall (?o - object)
                    (not (lookingAtObject ?a ?o))
                )
                (increase (totalCost) 1)
            )
 )

 (:action GotoLocation
    :parameters (?a - agent ?lStart - location ?lEnd - location)
    :precondition (and
                       (agentAtLocation ?a ?lStart)
                       (headTiltZero ?a)
                  )
    :effect (and
                (agentAtLocation ?a ?lEnd)
                (not (agentAtLocation ?a ?lStart))
                (forall (?o - object)
                    (not (lookingAtObject ?a ?o))
                )
                (increase (totalCost) 10)
            )
 )

  (:action FaceToObject
    :parameters (?a - agent ?o - object ?l - location)
    :precondition (and
                      (agentAtLocation ?a ?l)
                      (objectAtLocation ?o ?l)
                  )
    :effect (and
                (lookingAtObject ?a ?o)
                (not (headTiltZero ?a))
                (increase (totalCost) 1)
            )
 )

 (:action PickUpObject
    :parameters (?a - agent ?o - object ?l - location)
    :precondition (and
                      (or
                        (and
                          (objectAtLocation ?o ?l)
                          (lookingAtObject ?a ?o)
                        )
                        (exists (?r - object)
                          (and
                            (objectAtLocation ?r ?l)
                            (lookingAtObject ?a ?r)
                            (inReceptacle ?o ?r)
                            (or
                              (not (openable ?r))
                              (and
                                (isOpened ?r)
                                (openable ?r)
                              )
                            )
                          )
                        )
                      )
                      (handEmpty ?a)
                  )
    :effect (and
                (held ?a ?o)
                (not (lookingAtObject ?a ?o))
                (not (objectAtLocation ?o ?l))
                (not (handEmpty ?a))
                (increase (totalCost) 1)
            )
 )

 (:action OpenObject
    :parameters (?a - agent ?o - object ?l - location)
    :precondition (and
                    (objectAtLocation ?o ?l)
                    (lookingAtObject ?a ?o)
                    (openable ?o)
                    (not (isOpened ?o))
                  )
    :effect (and
                (isOpened ?o)
                (increase (totalCost) 1)
            )
 )



)