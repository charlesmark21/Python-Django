from active_projects.clacks import question
from active_projects.clacks.solution2 import block_collision_scenes
from active_projects.clacks.solution2 import mirror_scenes
from active_projects.clacks.solution2 import pi_creature_scenes
from active_projects.clacks.solution2 import position_phase_space
from active_projects.clacks.solution2 import simple_scenes
from active_projects.clacks.solution2 import wordy_scenes

OUTPUT_DIRECTORY = "clacks_solution2"
ALL_SCENE_CLASSES = [
    question.NameIntro,
    block_collision_scenes.IntroducePreviousTwoVideos,
    block_collision_scenes.PreviousTwoVideos,
    simple_scenes.ComingUpWrapper,
    wordy_scenes.ConnectionToOptics,
    pi_creature_scenes.OnAnsweringTwice,
    simple_scenes.LastVideoWrapper,
    simple_scenes.Rectangle,
    simple_scenes.ShowRectangleCreation,
    simple_scenes.LeftEdge,
    simple_scenes.RightEdge,
    position_phase_space.IntroducePositionPhaseSpace,
    position_phase_space.UnscaledPositionPhaseSpaceMass100,
    simple_scenes.FourtyFiveDegreeLine,
    position_phase_space.EqualMassCase,
    pi_creature_scenes.AskAboutEqualMassMomentumTransfer,
    position_phase_space.FailedAngleRelation,
    position_phase_space.UnscaledPositionPhaseSpaceMass10,
    pi_creature_scenes.ComplainAboutRelevanceOfAnalogy,
    simple_scenes.LastVideoWrapper,
    simple_scenes.NoteOnEnergyLostToSound,
    position_phase_space.RescaleCoordinates,
    wordy_scenes.ConnectionToOpticsTransparent,
    position_phase_space.RescaleCoordinatesMass16,
    position_phase_space.RescaleCoordinatesMass64,
    position_phase_space.RescaleCoordinatesMass100,
    position_phase_space.IntroduceVelocityVector,
    position_phase_space.IntroduceVelocityVectorWithoutZoom,
    position_phase_space.ShowMomentumConservation,
    wordy_scenes.RearrangeMomentumEquation,
    simple_scenes.DotProductVideoWrapper,
    simple_scenes.ShowDotProductMeaning,
    position_phase_space.JustTheProcessNew,
    mirror_scenes.ShowTrajectoryWithChangingTheta,
    pi_creature_scenes.ReplaceOneTrickySceneWithAnother,
    mirror_scenes.MirrorAndWiresOverlay,
    pi_creature_scenes.NowForTheGoodPart,
    mirror_scenes.ReflectWorldThroughMirrorNew,
    mirror_scenes.ReflectWorldThroughMirrorThetaPoint2,
    mirror_scenes.ReflectWorldThroughMirrorThetaPoint1,
    simple_scenes.AskAboutAddingThetaToItself,
    simple_scenes.AskAboutAddingThetaToItselfThetaPoint1,
    simple_scenes.AskAboutAddingThetaToItselfThetaPoint2,
    simple_scenes.FinalFormula,
    simple_scenes.ArctanSqrtPoint1Angle,
    simple_scenes.ReviewWrapper,
    simple_scenes.SurprisedRandy,
    simple_scenes.TwoSolutionsWrapper,
    simple_scenes.FinalQuote,
    simple_scenes.EndScreen,
    simple_scenes.ClacksSolution2Thumbnail,
]
