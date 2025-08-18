from io import StringIO
from scm.plams import Molecule, Settings, AMSJob


def main(text):
    """
    The main script
    """
    # Read the molecule
    mol = Molecule()
    infile = StringIO(text)
    mol.readin(infile)

    # Set up the MD
    settings = Settings()
    settings.input.ams.Task = "MolecularDynamics"
    settings.input.ams.MolecularDynamics.NSteps = 1000
    settings.input.ams.MolecularDynamics.TimeStep = 0.5
    settings.input.ams.MolecularDynamics.Trajectory.SamplingFreq = 20
    settings.input.ams.MolecularDynamics.InitialVelocities.Temperature = 300
    settings.input.ams.MolecularDynamics.Thermostat.Type = "Berendsen"
    settings.input.ams.MolecularDynamics.Thermostat.Temperature = 300
    settings.input.ams.MolecularDynamics.Thermostat.Tau = 100
    settings.input.ams.MolecularDynamics.Checkpoint.Frequency = 10000
    settings.input.ForceField.Type = "Amber95"

    # Run the AMS MD simulation
    job = AMSJob(name="NaClwater", molecule=mol, settings=settings)
    results = job.run()
    print("Path to RKF file: ", results.rkfpath())


if __name__ == "__main__":

    text = """System
    Atoms
        Na -3.307984867989309 4.665211407614774 5.251579466053888 region=Builder ForceField.Type=IP ForceField.Charge=1.0
        Na 8.267368484754513 6.371503475665869 4.675660223754705 region=Builder ForceField.Type=IP ForceField.Charge=1.0
        Na 6.241897202502541 4.618148168402835 9.234796987012643 region=Builder ForceField.Type=IP ForceField.Charge=1.0
        Na -8.895532175785883 7.763596643004207 -1.173375402991997 region=Builder ForceField.Type=IP ForceField.Charge=1.0
        Na 4.915666374535903 -2.561076822189959 0.3832555477985536 region=Builder ForceField.Type=IP ForceField.Charge=1.0
        Cl 7.070220869477247 -3.385218397324887 9.253245004138604 region=Builder ForceField.Type=IM ForceField.Charge=-1.0
        Cl 1.311759721323258 -8.056121340180921 -9.099552022644028 region=Builder ForceField.Type=IM ForceField.Charge=-1.0
        Cl -1.117431383638206 5.554988508013128 1.806323657551233 region=Builder ForceField.Type=IM ForceField.Charge=-1.0
        Cl 3.189610452598285 -3.824547937385274 -6.081045625431574 region=Builder ForceField.Type=IM ForceField.Charge=-1.0
        Cl 4.029661290942884 -6.175591038156312 4.215897839800898 region=Builder ForceField.Type=IM ForceField.Charge=-1.0
        O -1.638965708475173 -8.304560335545137 -5.399693558676732 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -0.6989562096625178 -8.22251553741089 -5.682334495416144 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -1.653339195974134 -8.926973139338454 -4.67018111310851 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 4.098221341011048 -9.324362104466204 -0.4688960685713048 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 3.563523625411066 -9.257782892426816 0.3120785568129236 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 3.91882848966912 8.823085360652057 -0.7946630635994122 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -4.45122339013087 5.530300122404838 1.369645343758375 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -4.657332705123082 5.947520375003525 2.222436772005635 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -3.444509176723679 5.498843574899521 1.374285273753788 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -6.821864330063607 -9.549455340763965 -7.887741046214142 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -6.611693043632988 9.066394567694381 -8.764950866127899 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -6.020996290936347 9.191290101146935 -7.396952931897783 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 3.115938194336389 1.706670678588281 0.75342748805247 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 3.588709443846407 2.483860975299691 0.3600826352458891 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 3.768408187666474 1.005601043728181 0.6088977477118908 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -7.347047655632259 -7.668498533714922 6.93046708541403 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -7.79455932955915 -7.909942197495226 6.071785870916318 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -7.861870697126264 -6.915075398324899 7.155147467806739 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -4.503337847256558 0.03693223043156789 -4.415054901130072 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -3.979156080294072 -0.1094003199119583 -5.173059490583826 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -4.931990164904431 -0.8034225759521744 -4.279937279826926 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -6.369391544404177 -6.10314186387046 -8.992530096881882 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -5.620851229432827 -6.604234591239234 -9.38217121155313 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -7.043642638923164 -6.808551156696684 -9.047820094796243 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 0.003795549234116662 -8.638666495882209 0.7533331892872563 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -0.7687732343691029 -8.048802725322787 0.7320566650677496 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 0.6630965162591207 -8.04795162318919 1.221525397963397 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -2.34675756992035 8.930146130050767 3.660900310448933 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -2.047828401648621 8.088971770965957 4.076409493437286 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -1.628987752030673 -9.43105605645335 3.804586909279022 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 2.243828423325957 4.187991831161167 -6.484485056065208 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 2.318734683333163 4.160095076032141 -5.510574624857361 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 1.660169195180675 4.922495364843648 -6.627601127338433 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 2.174868606310292 7.560604226125383 -0.7480227941309863 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 1.343996462026106 7.202820033804404 -1.096922159209591 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 2.128286379615918 7.132485907329932 0.1391882318986387 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 3.189875650430659 8.744363396035048 2.196605255141561 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 2.269668019240405 8.621513810962995 2.566257659456736 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 3.667836657822788 8.996923596474948 3.005591091997017 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -2.323354641309543 0.5639548531990728 -2.818083409142565 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -2.545447251074854 0.5882490015287007 -1.878307313299879 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -3.2036722558546 0.4628164178016149 -3.279517408997646 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 2.51402484625339 3.392359382905991 2.889843448143062 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 2.244755887164111 2.955999391680086 3.774732167570762 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 2.576142788186585 2.630362170148082 2.253936528652266 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 5.210834485877153 -7.659736750166851 7.764775014786822 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 4.921111904434225 -6.706761234377728 7.865952920031616 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 4.960531884006246 -7.753860192363071 6.831064025452655 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -5.370228113711227 1.661248382966231 7.436390144401797 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -5.236058212128718 1.797719939371765 8.342583625390578 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -5.584972979348956 0.7142419429228422 7.360020073371047 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 3.229025921594264 0.9165118808082244 -4.646837812546581 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 2.483384210950065 1.539348028384809 -4.84661209123323 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 2.799739531890971 0.2352588182111834 -4.132526382123689 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -7.104537747117833 -1.604665439769136 7.09122720219177 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -7.302660761249429 -1.728445454222934 8.029182231375154 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -7.80217187720903 -2.08206474966434 6.691987916921655 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 7.903959327752319 -9.503980448054964 -7.882247634441207 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 7.185225939503872 -9.079568240542542 -7.338157229905846 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 8.682653209019504 -9.322923473263142 -7.425216329788415 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 5.646508616182192 1.789996279216629 5.015756231250863 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 4.77812576346567 2.09327853340372 5.063151977785115 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 5.553064245360971 0.8421867756155172 5.101413523188807 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -8.503054869731107 7.207039884254563 -4.996026413718403 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -8.320990512733774 6.885181153107787 -4.10984832965576 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -9.413438557329789 6.939882302078409 -5.182685497334365 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -3.364859281487327 9.048976363200067 -1.230039983984538 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -4.046842605646344 8.602971471578737 -1.839330745112465 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -2.662554798787731 8.368462536132574 -1.210952829695486 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -8.89795951156629 0.6720729387623189 0.65753524015 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -9.353348256114966 0.003419735233299131 1.214515427984513 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -8.406621029167026 1.23358674699581 1.262732738590238 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -8.064789778265373 -2.429394240165403 -3.788185433411088 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -8.030861838504011 -1.518865700036845 -4.24792017772699 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -8.898383013657865 -2.807521802683368 -4.115757647435903 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -9.049519259992675 7.062749689907633 6.262786776313596 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -9.264927171699613 7.583557274217552 7.056017086569412 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -8.123966308588837 6.835175459136886 6.285456694400072 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -4.096444002963606 9.091426320837344 -6.212791904244865 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -4.855314273034537 9.309276996749045 -5.582089961986176 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -3.52539052022688 -9.145714073280439 -6.168769990062334 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -5.026953026718775 5.194879531470495 9.34032350692863 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -4.079277243361644 5.467743352484518 9.303721412557481 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -5.061543467564437 4.55383738170349 -8.893461143486421 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -4.354515802759551 3.0608187843132 -1.743597602849302 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -3.825406598307003 2.438569018321004 -1.228611174450658 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -3.625590797827771 3.592877906141009 -2.121495804206156 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 6.600819436889913 -8.770843477763259 -1.272125154145245 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 6.71333480260209 -8.542111997160537 -2.207809842517798 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 5.65552250070384 -8.937548205204251 -1.044157658231503 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 8.576654287861285 -4.423613677379945 -4.819200728222373 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 8.856910463205212 -4.453732036063759 -5.709512605379629 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 7.609550308551627 -4.532727307160946 -4.866938323005016 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -0.3202811237321522 1.746716677526389 4.772089868287063 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -0.9329149587249762 1.264480691783478 5.285362700217986 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -0.5897386766131778 2.641084313676882 4.996352490790341 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -0.2042598920156618 -5.223255011619396 -9.090693318593708 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 0.2592455867751255 -6.086395685054652 -9.261895388981472 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 0.1664519768327586 -5.007505178815621 -8.239983989208486 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -9.359031361934466 -5.324608832477061 4.902891183409217 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -9.164245823900067 -4.908253273519019 5.790560447943015 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 9.085144458993224 -4.692896910061911 4.512171553522307 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -4.28525669167574 -7.221782534403007 4.402669381315379 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -4.248444977821295 -7.234984142053532 5.387550382031918 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -5.104774279458531 -6.777647985277452 4.320544623975045 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 1.080812998874785 7.631378031479015 -9.369007072635812 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 1.181833840001164 7.602132369656662 -8.406712017813055 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 1.118219094915967 8.614205230477401 9.427869482435918 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 4.979412701450611 -1.578710894019351 -7.682814284267579 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 5.313969788417056 -2.062656460385821 -8.426088323219393 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 4.450449239416769 -2.233866392747906 -7.25021110712566 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 0.5926910591481895 6.562336140777148 7.100105681420681 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 0.2446672943210487 5.708194443013872 7.348122355292326 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 0.8476691042130384 6.973799606638233 7.947141301216825 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -7.980313214268569 5.81590486714495 9.271208313740395 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -7.09880485426499 5.607499555377046 8.935041471564173 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -7.760138673457512 5.760475242263989 -8.802320828608103 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -7.385249195726063 -2.182933636569523 0.6529169736943383 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -8.107154234107544 -1.969724492698457 1.214233082874503 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -7.756238065047726 -2.756270450497496 -0.009181373701427745 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 1.998065764602631 5.669342130287672 1.425971239327738 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 1.045205483671633 5.739026220704956 1.654154502849113 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 2.208698313381999 4.906703492306785 1.994038032397064 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -2.194113790567656 -1.356242638650919 0.8956443348002999 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -2.469927029202249 -0.6249719592951323 0.3893624734402172 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -1.287373336073283 -1.467298754620388 0.5772460733610124 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 2.638130662290408 -3.762010196508163 6.144610611631377 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 3.53544720735375 -3.878326426583073 6.590945577904641 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 2.71465228171468 -4.385797755839139 5.444949226932124 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -0.3576060130174758 -8.175924407017838 4.048308423948749 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -0.7716556733301024 -7.615848724031138 4.770645314246646 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -0.3827008516905405 -7.610688396824093 3.262619386850781 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -2.635203508331306 -6.871808691515724 -7.504901991257023 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -2.402242581149715 -7.224501257063331 -8.423329715568306 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -2.240866230192747 -7.451862059717057 -6.893621727187529 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -8.547108763567806 2.555455129839356 -4.881715286530308 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -7.552789650632717 2.60065862065009 -4.762522058277222 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -8.731026728672674 1.572564388265836 -4.827643095881099 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 9.118950264265152 8.207824429022708 8.942711166835874 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -9.071055851017565 7.881403854119687 9.349211257149371 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 8.746951662126298 8.764017073543785 -9.371821023939503 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 6.332462412848852 -0.0678319452128857 -3.911322479054954 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 5.421563781890949 0.02425643110639782 -4.146357203168371 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 6.709396796398803 -0.1200970526003152 -4.807302929852551 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 5.481324965657016 -3.896882808682196 -1.706668836338143 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 5.905074652121808 -3.397271802706353 -2.413819474508783 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 5.135748422673396 -4.652282961611113 -2.157751979624861 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 1.216201913855887 -6.417753002510262 2.045655069769634 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 1.782226980124896 -6.401611966568303 2.884976973031204 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 1.519711483993549 -5.604706431108002 1.569913027051342 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -5.517955550820846 5.413053335094822 -1.680317927446508 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -4.684918525877636 5.874795703163167 -1.88748884703751 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -5.225127341379738 4.491031020024757 -1.534270924882181 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 5.936644801284475 -0.8985411883346652 1.501092442200972 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 5.593310146365586 -0.744007209835213 2.422559921598458 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 6.931139010174483 -0.9451494909511094 1.631070481035332 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 2.374650871208009 -1.487398793105792 -3.513825162744886 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 1.502716044173158 -1.847416185308158 -3.247409487574766 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 2.71786378580832 -2.217532509998655 -4.054655795570618 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -0.6660151881873067 8.430993740056618 -3.461094662306132 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -0.5486360830449963 8.535325343067599 -2.514430163472766 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -0.5825047926178284 7.483405127636123 -3.573962936118312 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -6.082765151301786 -9.561294006117278 -4.404400544721918 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -6.925762619336347 9.06039852949892 -4.038246715905058 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -6.087144484797537 -8.638743189262266 -4.233774851333527 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -8.465589589421008 -2.040645841698594 -7.299874646621578 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -7.659628618142607 -2.530716098647458 -7.120719321645066 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -9.107354904562794 -2.762917062025506 -7.323269698280161 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 6.508038062010026 -0.09388994826498011 8.316973791417182 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 6.633418240855568 -1.004883062227659 8.678019937696625 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 7.336629897437423 0.1129548577075589 7.823403955514991 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -2.032447522740481 -4.49320937230107 3.460615645357795 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -1.458265227314586 -5.232762738199877 3.622466008716057 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -2.565088277799201 -4.440141387205428 4.270556721663707 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 3.350913467205419 -8.009952136347508 -4.514751476627608 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 3.353746880032614 -7.101509697454546 -4.112037217955148 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 4.230287444359741 -8.269691420140241 -4.541074788550784 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -5.922445065736418 -8.290945328306403 -1.097896133462918 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -5.093208544024927 -8.812658936093712 -1.13584861804405 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -6.284124887743813 -8.662108896470725 -0.2327731297846344 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -0.1622793021633993 0.7631574337450784 2.211759685902608 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -0.6688899327780945 -0.05846617545565588 2.223520640866069 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -0.2583241600438099 1.080207264356336 3.144925228049164 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 1.228013596547021 -8.211874719641521 6.634665106376088 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 1.243836647321113 -7.325901861556337 6.280274357090311 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 1.454226029734814 -7.922876393432464 7.535118545319423 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 4.829834767525968 5.636748322009502 -8.296921096644436 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 5.109079783732858 6.321672044015161 -7.714978203513557 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 4.03024425604275 5.360051453478245 -7.86066335219803 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 2.610762942709918 1.582818664922122 5.185261153249146 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 2.904053919365837 0.8643493989876559 5.78145459459283 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 1.654357697301919 1.587093713789067 5.281767844777967 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 7.241716535620656 -0.540418981379945 -6.372074512676546 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 7.746435783452021 -0.06298178689203564 -7.016994119867076 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 6.685531211041337 -1.164745290399042 -6.874298488967575 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -9.44271045016079 2.608824538299845 8.825017286254656 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 8.7130241174548 3.024348238915931 8.623096828668556 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -9.315074281184733 2.885681787506832 -9.247803416070317 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 4.921655355028959 -4.708229616512178 7.755416581038037 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 4.489386379302677 -5.040620412287773 8.581671938037845 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 5.698364785903339 -4.156707208556138 8.073870139836654 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 4.125177496067787 -1.153434950961811 -1.241743148803939 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 3.520792432041413 -1.249945218036269 -2.027947649208226 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 4.582616646079645 -0.3060942085081064 -1.447859581130165 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -0.6160847849348221 4.186726719943122 -8.522770556645083 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -0.6027564127786402 3.397334336172896 -7.937657840418511 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -0.5557894303311524 4.87058403230669 -7.814825276965647 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -1.259406124333129 -6.19228493483614 5.620741400923515 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -0.9669050976593581 -5.451535189806716 6.239130955709265 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -2.093245061282879 -6.471416784621137 5.990766045095016 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -3.135942478236556 3.049301280037917 6.911916670387116 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -2.374210974468365 2.764896235431559 7.450549667078293 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -3.85656047235733 2.387856204747047 7.136570713966729 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 3.748608947337944 -5.530835906686144 -3.381564004163939 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 4.018433027960216 -5.119334322559497 -4.225865118132365 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 3.013000419442252 -4.962311097520984 -3.059945728441669 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -3.330515721746443 -3.156287771283057 -5.457499244566922 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -3.034688592089534 -4.050309749171104 -5.123022880618511 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -4.052804854897742 -2.922434257844752 -4.853337466489119 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -6.283737867261633 2.162575114079984 4.582466016212155 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -6.186768107630691 2.349039810995733 5.527755955715463 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -5.496865349934708 2.496924682114884 4.189359055294657 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -0.7730807014949549 7.89686662260275 -0.6460878171828359 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -0.871500277126524 7.107709517881514 -0.03453075521291851 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -0.5249499563792506 8.605219960795976 0.002182112905809673 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 5.078729935573911 3.79251132674226 -0.02318013289156639 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 4.793749312436755 4.287514651524649 -0.8150900396709033 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 5.322476544815583 2.914153835078895 -0.4389455581711751 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 9.251422055583724 -5.883456897039109 -0.8717843113917446 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -9.046845915918357 -5.171116456227354 -0.8443607107242025 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -9.603954791158312 -6.327881481573241 -1.725740681397827 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 3.474942460014607 -5.485164891392984 -8.955771377935568 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 3.430403140724028 -4.811772492799817 -8.258956360799752 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 2.752522944243783 -6.133174072690026 -8.782607028445168 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -5.21640988434067 -8.41568309383959 8.287808982354184 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -5.507565214236825 -9.243173186787947 8.739042573206495 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -6.025399788239113 -8.159993142401655 7.825917011489101 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 8.230865840496699 5.711284063868478 9.076242270099446 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 9.22023620700419 5.520335107778212 9.102868347584746 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 8.181954449631696 6.695498148094781 9.018482972328608 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 8.315724060867842 1.748153777253636 -1.266319256632131 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 8.974056047849142 1.34165652669592 -0.7380876252440383 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 8.751519464489368 2.521970738614136 -1.660761199398577 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 2.163972355358059 -1.523728922610433 4.50508687249305 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 1.216279788369786 -1.753485600840163 4.408605364078173 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 2.411324851569692 -2.145049225657191 5.188696443037752 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 2.525251244265999 -1.589546896279442 8.258404629209465 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 2.317642413624557 -2.534616832443581 7.913078954493056 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 2.169878527972086 -1.65223958459149 9.141776545924149 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -2.837501028364426 -5.517449597229336 -1.2625416431197 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -2.950259172669256 -4.966452354269695 -0.4717939834708654 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -2.689669198297938 -6.424185515741497 -0.9081074293462909 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 7.868342731045747 6.587506192396256 -4.677057403063675 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 7.768492170755279 7.198301712603583 -3.908039745503006 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 7.152138668688661 6.966768683853472 -5.274218595498149 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 1.263281340266591 -2.362467755266729 -8.325689078219444 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 0.4571561604474332 -2.683022448069553 -7.900578636444468 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 1.979749976036048 -2.709077990517427 -7.728176783546597 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 0.8240412756874683 1.376305411473902 -0.1852344716567851 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 1.732449276489194 1.498232701509578 0.1711932120602515 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 0.4004545867933358 1.136776478417604 0.6269856913811381 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 8.444477999758792 -2.685348339248275 4.235912860006755 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 8.922342655992052 -2.372495224436137 5.043322783192956 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 7.590499871560716 -2.847010130030761 4.613985284387325 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 9.203457811412312 3.970482906600537 -2.968817750828622 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -9.308895885677103 3.462510326941995 -3.676383947920446 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 8.70027630601259 4.610865137246656 -3.474530628220982 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 4.035189883358146 9.422146177236534 -8.421062496519122 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 3.595380415200097 8.655998042962356 -8.939006263098738 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 3.392153915281063 -8.835733831701894 -8.704087154128985 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 1.632663788894429 -8.321774141616503 -1.671769971895817 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 1.338321694075298 -8.741260025095585 -0.8315565341175308 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 2.486190871237663 -8.056987519793491 -1.466496464605979 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -5.116377671052278 4.624101837069362 -5.956903527362159 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -5.068003375208124 3.936923120016036 -6.63906638183007 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -5.140170500963394 4.157923700032373 -5.095037841781467 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -2.310172912023714 -5.611287766341052 -4.793501731335843 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -1.363391567005697 -5.426392604464276 -4.88546957163646 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -2.304763969482778 -6.572360657538182 -4.885519125898035 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -0.8131952940216205 -7.553683499551854 -2.493119129064414 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 0.0822709532698825 -7.767921349018927 -2.204192031673376 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -1.119171579900066 -8.318481483044858 -2.972911424010362 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -7.84040893524266 2.438136045260278 2.440954448354328 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -7.321762652066294 2.894656089667137 1.768806981689621 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -7.227983623219215 2.472611719729582 3.216236074355946 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -3.366420503620494 -6.965985397872454 7.139163110731748 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -3.919177787590353 -7.640330415219867 7.521821032066459 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -3.847642980304407 -6.193496431128363 7.495757936441009 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -7.100668180069211 7.285634755957351 0.2983545721511555 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -7.012947989338753 7.863479102363492 1.032722450315445 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -6.317144003753705 6.745979047247602 0.3536378106186652 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 3.074668729164862 6.84366918444118 6.00774461087151 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 2.139721289671088 6.889960433856697 6.270066905211227 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 3.301737455396672 7.751237738094227 5.785457353145289 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 1.787278582957163 4.358483611014027 -3.773009458517767 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 2.265861718533569 4.520379642360522 -2.956213244855042 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 1.187440664025662 3.66212263563063 -3.507624130868185 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -5.6822444000375 4.704356000750768 6.335661164577356 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -6.633585518772561 4.652380461833578 6.18201222455339 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -5.594142042542546 4.388770662996133 7.213204516867025 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -9.278943724089117 -8.257966916268391 5.298210075194267 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 9.061490839434359 -8.287457095193011 6.039673687696035 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 9.299764510479662 -7.61575789781083 4.718893535059625 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 7.919526319675363 2.470675313520482 3.507531320507478 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 7.288782291291413 2.622180210340303 2.784053410780339 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 7.282552956335237 2.04528390613947 4.130196012321199 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 6.16898459888275 6.983465531273146 -1.088557312050052 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 5.522573292098411 6.784188867897583 -0.4017695596706392 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 6.990614100329667 6.58945800549768 -0.7364670665205797 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -2.219839740421492 -0.3802446830959104 6.411177028917916 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -2.173778026807082 0.1088254152760135 7.24378729613485 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -2.505566786922726 -1.248550431946432 6.658729574808413 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 6.122766577633591 2.681212555521017 -8.3955607471449 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 5.504530836755547 2.00013112391371 -8.08666632445509 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 6.409019154418709 3.043845569200451 -7.503517749653763 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -1.095773884653223 -0.3051914117652126 -7.098505078881709 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -0.5109274376904199 -0.2636532880969547 -7.870834695231239 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -0.9595335591784717 -1.242245464136922 -6.820595903541703 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 9.129815256048811 -2.22501397626474 6.890831434445927 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 8.494238855316665 -2.57075485952506 7.573409856794822 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 9.060536349528681 -1.195175467592132 6.929044322096677 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 1.998375236744445 -3.975220086139398 -1.818122656649502 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 1.054168363141879 -4.13634377184992 -2.001971546794082 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 1.968417677190921 -4.056746273693691 -0.8443565393497054 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -2.902540203011435 -7.655504012559635 0.1083745122693255 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -3.43058905991663 -7.928146088850016 0.9223874663957746 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -3.108362724745725 -8.370723037287137 -0.4861460967741524 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -3.31825858447543 -3.841486102080469 0.9467896989044373 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -3.136755227010071 -2.892807994654591 0.9898538991831449 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -2.766331289427584 -4.192575730110777 1.668634486676323 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -4.117675442536406 -8.812188775651093 2.288617144823249 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -3.359543502822121 -9.31161461051955 2.585036924041337 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -4.357509331504744 -8.293714192453233 3.069472878319101 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -3.252696344069585 -3.014824071545955 6.888676715251743 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -4.042929247245862 -3.498807851872904 6.548391434136645 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -2.647023607766256 -3.753640494058763 7.077451502599995 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 2.457279889084823 2.984972216099058 8.099634478917784 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 2.852762219930066 2.134270515478989 7.80961916072946 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 2.343744981500573 2.810944965137733 9.082144594823175 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 6.191219673410773 -6.121544570028699 -8.321532045523561 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 5.341246930841465 -5.94729198786008 -8.7463494951414 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 6.65590447770748 -5.396571031307765 -8.762834807955048 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -0.5916989404947783 5.680593715624641 -3.797045339553339 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -0.7397619978055149 5.380361852479639 -4.698545153246778 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 0.2209116982339087 5.229222878277418 -3.510415403172775 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -1.012318144280531 -2.973502519834509 -6.658843873835867 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -1.951852052279838 -3.048665106117511 -6.342936860251588 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -0.5888957577877679 -3.786347420924275 -6.414852458589523 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 0.4258014187026092 0.5451296308789447 -9.535384881613423 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 0.8326177536805797 -0.1038368957009758 8.948177328928608 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 1.175500569538586 1.066990429765677 -9.145995142794906 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 7.080636343140441 -7.966650982328883 2.918641849951993 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 6.25189479000097 -7.723406084257578 3.298974169550053 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 7.041630129739164 -7.284765403476998 2.194360595848604 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -5.927499278926369 7.60659368105833 6.356454594491216 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -4.972963365244602 7.437432567987986 6.261607806440492 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -6.21422940062302 8.003690796820731 5.528263060628714 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 3.848987810760283 0.5651936829411366 7.615855830607762 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 4.747682547674008 0.350143409342123 7.766803428184602 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 3.435731225365592 -0.2443076192547048 7.949183215767954 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 6.56590977684536 6.724103446857753 6.308737076662969 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 6.20557713389585 7.377112567312938 6.882574434645597 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 5.779392367566591 6.138645791918127 6.122715629437381 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -6.110894323079141 -4.258876147445997 2.337196373366595 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -6.107206161416096 -3.281998110959814 2.579636859572815 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -5.269814323375157 -4.374310975243003 1.824121288013818 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 8.873278439961689 -4.229986347249969 -7.471369949069936 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 9.161436416205733 -5.042634491529586 -7.903502788480333 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 8.092065214922723 -3.864511651901458 -8.028764961498121 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -4.063114072488367 -2.206715820389374 -9.492935323686071 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -3.491667939625789 -2.934239734292953 -9.189085073257456 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -3.989582222238818 -2.349320112984512 8.540527302810974 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 2.279161981736278 2.326480789371105 -8.385742358341551 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 2.85883955437029 1.712291561305781 -7.943829176596776 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 2.241262435874714 2.999728749426266 -7.70631854632796 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 0.7566922243477282 4.330656788778649 -0.8966782359406487 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 0.6216973661394009 4.70882967646543 0.006676763845137797 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -0.0244682379270886 3.789973286842703 -0.9563681117418383 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 8.053718278368908 -1.434319072164175 -1.991929611562544 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 8.808374882681933 -1.445973576392711 -2.591136006303731 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 7.321992232925752 -0.9637063170328434 -2.381384274725035 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 4.574822344299699 4.669271932287868 7.309705175319196 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 3.952820306574365 3.918750446425204 7.472260370693092 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 3.916110671031226 5.277210836888727 6.884566872062774 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 8.527689613331486 8.515637344288466 3.632507845780764 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 8.88371427196514 9.114313970203389 4.312564220936747 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 7.653038139580181 8.981200320896946 3.477530328994792 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -6.611038530646843 -5.916446114246773 4.284260197287399 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -6.560570770227618 -5.360948752728175 3.498269832331188 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -7.558235799523555 -5.878611646335077 4.512224497897543 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 4.906192325481438 -4.829306783745857 1.546867612190464 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 5.644015510247927 -5.394279273593761 1.201479630910723 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 4.683850392238363 -5.232943535777035 2.469605433347626 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 4.211670781736389 0.9965380637660198 -7.258214336887709 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 4.416830556502154 0.01757063243744062 -7.467399329655882 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 4.056141864063878 0.9468683499950501 -6.261573620717649 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -6.604084653743192 7.867899500797368 3.768466024682711 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -6.508504936773384 8.704498198517477 3.313181987763142 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -7.567272679637827 7.886502412390552 3.94592691113434 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -3.034484345844689 6.926970928916507 6.120929014454933 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -2.653412943349 6.630071998139775 6.986387227074279 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -2.604982426674058 7.76498480625299 6.08609068976958 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -2.538236594493983 4.927567983109861 -2.014205965939843 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -1.9034027837556 5.302614955457688 -2.716361576165001 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -2.229562051243366 5.382948298785736 -1.203989961914354 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -1.769886599331466 -8.322111178367965 9.302885630325999 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -1.987073771813023 -8.001204336210808 8.392166159917036 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -0.7941610793099005 -8.352538477295036 9.341179530493054 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 8.61197959685185 -1.497904066385135 1.772035034076655 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 8.407411617386742 -2.338736738697062 1.250164890573092 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 8.742095283813599 -1.902467935550114 2.734603627953412 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -3.739333111146557 2.777949228119752 3.743919344408473 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -3.463972326904146 2.982495738103665 2.782141758152521 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -3.514669460027022 1.768219690733503 3.771081264225279 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -5.411443278807493 -2.621882989551504 -4.010100443546104 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -6.3699218689446 -2.719223114355407 -3.942943104155622 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -5.12200049022666 -2.671006467159682 -3.097434228197681 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 5.643292650769975 -8.355515201294656 -6.476400940307525 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 5.093828746394767 -8.708866066665399 -7.228580634869171 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 5.975059325348914 -7.535228326243017 -6.933487369752227 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 6.846261154652519 5.808181976006321 2.802076860520289 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 6.537177654332464 6.411400624839128 2.099056141618925 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 6.045167445971455 5.317205867333584 3.117625236478529 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 6.214757453593754 2.898216350769759 -3.632863037411562 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 6.516474219805432 2.054284568163109 -3.888743670124208 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 6.822687745435958 3.119403779890868 -2.947044050383111 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -9.60291620747784 -7.024175970961986 -3.477143864021172 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -8.772900516818103 -6.84006499029069 -3.934298640067817 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 8.758193207237001 -6.363616684514428 -3.875631446851816 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -7.979385334571411 5.944238338851074 -2.515143180301922 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -8.450231199520035 5.071288567778988 -2.563546954930023 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -7.150552792066327 5.773605254283285 -1.929735837445313 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -7.997179189898808 -6.905675438581286 1.083808968181459 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -7.724317432435011 -6.028609737455522 1.357480593579939 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -8.535959533752386 -6.698302514292833 0.2761631711260485 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 2.880316221806546 8.45839309827976 -3.4447482547452 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 2.448917128711416 8.358360845104983 -2.604333661158744 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 2.625492608627626 9.374644907384415 -3.609041532330366 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 5.307863882275979 8.07416774026979 8.415036631862273 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 4.985090191858243 8.958533682680514 8.50499910892594 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 5.441650877497224 7.723319618849244 9.25094702599937 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -4.829049819332995 6.039993185385008 3.957941417229384 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -5.357408835809507 5.42798934876901 4.463432535138348 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -5.405946148499109 6.837424716908632 3.866813558844109 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 6.976315286008627 -8.47952695042474 -4.089602006060809 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 6.531578827263505 -8.252050747137051 -4.904401639191353 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 7.82348284595903 -7.981750953557367 -4.196245099981163 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 0.7725329951790167 8.167138446283534 3.000926240683106 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 0.4549897764517934 9.113912639027193 3.02583800596292 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -0.04124017128196344 7.610220612713716 2.93331367966137 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -8.974385591664623 1.362115652940784 4.99323721313817 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -8.115963664376357 1.381227221650981 4.511218692024867 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -9.633264372642529 1.742616366010954 4.376718885533908 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -5.962544938175563 8.066864345107556 9.054706897295151 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -6.113088069954323 7.968897952940682 8.057355283096447 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -5.871748110380393 7.129719806656301 9.376588118271121 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 8.203014753672893 8.574722158654334 -2.614117226514629 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 7.938486898876842 9.287462793370146 -3.236070503841841 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 7.384085471963924 8.511824524201021 -2.137244266263433 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 6.828014627976996 4.150217237593062 -6.171418105724303 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 7.129000217262237 5.041276882952427 -5.818994287418714 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 6.584259451028976 3.726629301148616 -5.344861813760843 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -5.488909634548812 0.4049238640327286 -8.596848797776321 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -4.944652332386756 0.2900593884048708 -7.805117791926128 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -5.525761961660754 -0.4991137931899832 -8.93975586084648 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -5.767007567433561 3.194614426399029 0.7101774302492054 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -5.337571726517693 3.171289832599231 -0.1354419452765784 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -5.05053763833292 3.527002896977865 1.216544909133868 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -2.487502623546459 0.6032560620650381 8.841289461659519 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -2.956045593321194 -0.09776945965514701 9.348217232504824 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -1.916246775733589 1.037294066258085 -9.474699259551299 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 0.3902181858774593 -5.195331699184865 -6.327431877869024 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 0.5666109759606915 -6.067206932175718 -6.017152169390304 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 1.274949156638243 -4.723867362242816 -6.304070476836684 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -0.617406206313094 -2.177113865850069 3.681720341840744 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -0.99471240808271 -2.977954404789745 3.247764590197998 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -1.38436998782017 -1.777548929255466 4.004846237827523 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -0.0876886302449445 3.853531960176467 7.779701706327534 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -0.2356570276992724 3.937925689982329 8.748518269127716 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 0.6873246047663617 3.276100219509781 7.7902347378589 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 7.847961997620857 -8.301397003066521 7.534889970031854 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 6.921284864419296 -7.980474206626804 7.751437342950376 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 7.881339771624572 -9.072331305904076 8.053316368058967 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 4.460839474344267 6.655949700732464 0.9937317386186185 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 3.9711688222655 5.819503522744651 1.011852731411677 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 3.813290453165442 7.349623713085415 1.322478992338569 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 0.5758983934673128 -1.206169833680659 -0.3325747502896131 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 0.9407431449085365 -0.2889583094906412 -0.5029317801501346 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 0.1415297928463147 -1.457513977204855 -1.196929875361986 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -8.264924916870115 3.946951196047051 6.436579907623715 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -8.546999297502637 3.521242804668435 7.311998907113273 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -8.545332640709885 3.314328985398161 5.832064979002599 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -1.280601715506336 2.349475833352213 -6.108163008631482 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -1.025564257317467 2.454474144611131 -5.184684950842125 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -0.9547487330425019 1.461134333867067 -6.365499075156944 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -0.5311889457235981 -1.932070798858929 -2.684951280103491 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -1.378837022279773 -1.461551622877248 -2.651717224703486 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -0.7611974082370764 -2.83885490115939 -2.791662887639004 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -3.189372067316742 0.2133970002217561 3.823950680931284 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -3.447275076735 -0.6328495801443734 3.394952340402456 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -2.824824109497848 -0.04037881241095358 4.66154670350922 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -2.03953529362978 2.683843458932607 1.482106347969084 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -1.34744173750002 2.207373114985599 1.946934003208226 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -1.657718912353286 3.61753562175303 1.37254465841088 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -4.517788833905412 7.485989659803663 -3.518317273535652 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -4.765573694394579 8.30533518267538 -3.989557232343459 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -4.413587822324136 6.839052048732171 -4.232234985209033 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -1.026597796907575 8.664669785043564 6.188149374777009 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -0.3499962779631706 9.278946160886662 5.913423740970255 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -0.4733111121435652 8.023750236272974 6.649099249101477 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -6.794008405858867 -3.450025560289986 -9.462850775667624 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -6.453829585324023 -4.282729963818065 -9.261493903131749 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -6.023291827430976 -2.87091312633141 9.320591939088047 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -0.8096445035706095 6.30209304737502 -6.746378954132051 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -0.5095579576393821 6.819592703772602 -6.006975507179656 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -1.291091965110466 6.97475328017041 -7.262946838905995 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 1.922802720092819 8.143555448660962 -6.395692699652511 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 2.728744031961691 8.720807376449246 -6.64975724344701 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 1.947049381636885 8.073789052224859 -5.416732884060941 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -8.181161075771509 -5.031527006025687 7.702365725494006 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -8.875255559479017 -5.408966625073554 8.311928112693787 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -7.828196990973844 -4.291384273139533 8.341299248080807 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 0.253884532206441 2.077358419919844 -2.982497435869897 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -0.6795672566309402 1.773647476361939 -2.981098635149686 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 0.6232479789496698 1.708442431885716 -2.136805223699955 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -5.134402020761343 -5.285321957927493 -2.852836529874477 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -4.704277693639871 -4.849851448453002 -3.576158418750361 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -4.406811250480021 -5.480908795779062 -2.236051619165797 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 6.834907666700571 2.817479302953088 7.811452794944104 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 6.580116497429613 2.500808578726893 6.942860368712031 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 6.50812030179153 2.113402614445284 8.364751907855773 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 8.955319663229059 0.5569998180103986 7.346280512022129 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -9.431601996005451 0.7894311271332294 6.582855618925898 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 9.215391271874383 1.174784817394731 8.022847088090357 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -6.640474103938902 -9.324773320374744 1.749256246431898 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -5.76133425871928 -8.96484286752713 1.810149864531379 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -7.160502969647266 -8.479762152855765 1.644097446264236 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -8.853275375911803 -9.255522683994716 -6.174921058389637 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -8.119644469145946 -9.317346309240126 -6.854560891696817 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -8.785638107387079 8.864052018737501 -5.798309125000212 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -5.544902611603042 0.05254381756303468 0.5727730333128683 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -6.109769772322676 -0.7667943340609508 0.4521802912655911 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -6.15967369461683 0.8185966801297907 0.621619351789932 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -2.206271359872707 6.225775422953319 8.700048423356112 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -1.490084842414212 5.764370224709263 9.198301762314298 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -2.351227171989917 7.036982664791578 9.259663735284626 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -2.640494574977415 8.271330401117835 -8.422786420367322 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -2.365698311601501 9.1410713512195 -8.812704564790545 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -3.373980767320748 8.547066295551936 -7.812610021137871 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 2.408460315226058 -1.86183737471342 1.689607772643795 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 2.086954899521176 -1.616165851414826 2.59441877061482 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 1.841836797475509 -1.431197822674755 1.07439029846618 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 8.891209657960347 0.3540372574070033 -8.257384182665326 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -9.594586210387929 -0.4841873088539292 -8.402145702227358 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 9.037514225043553 0.9913554775619002 -8.970437626139026 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 5.182654147011812 7.371432506532893 -3.740699423420918 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 4.326581560037111 7.831121273838071 -3.448806158710184 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 5.476938065018436 7.075851674969809 -2.817528707476729 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -6.983903504182429 -6.014644381889342 -4.809215600585391 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -6.545338379398009 -5.503847020488864 -5.492598000221582 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -6.370374090263321 -5.935491557026086 -4.087400327529096 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -0.6222918665257652 -4.849743563287871 -2.640171149368539 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -1.504056100274526 -4.957575890716225 -2.404492863425203 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -0.2795179262750594 -5.743018450450671 -2.527983560022456 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -3.131120942275579 1.014678354201427 -0.354883731439128 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -3.899811776749291 0.8097013786607119 0.1761626558992811 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -2.601194224781857 1.42072777827957 0.3304749115536071 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -8.976692840933035 3.099734637494135 -7.624153212913638 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 9.088697399773688 3.114424755351144 -7.359826987198462 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -8.527701643594668 2.965171153631126 -6.765168029182258 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 5.757453127306928 1.047979042842768 -0.8010486948742065 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 6.654317966263346 1.373377920906633 -1.118674432394768 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 5.927706253903239 0.4836212116321553 -0.04794935348871093 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -4.724656735571284 -2.578512404106319 -1.356056994623062 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -5.553953938266197 -2.468336818065875 -0.8970836249338303 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -4.23620671072855 -3.086756481023321 -0.7528801103922838 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -5.679736092246384 -4.279600835279695 -6.670770333899815 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -5.737369831112399 -5.062519483044013 -7.237965468225264 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -4.707693154794699 -4.213415587605384 -6.547216820670951 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -0.9566572180114076 4.457890625479964 4.63552353691138 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -0.2527921206945563 4.81383576601034 5.184973887615496 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -0.8361733413793265 4.785742724890321 3.710571608037472 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -7.967994715336884 -9.091845169390966 -2.387390691251785 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -7.290028390690785 -8.553971571263046 -1.895273583395987 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -8.636572793481424 -8.416956834606889 -2.56934604425003 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 1.047713776742339 -7.74242261902114 -5.912191528918133 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 1.176095459917279 -7.954827508368083 -6.873767282801908 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 1.908516735588295 -7.721025891324149 -5.556093700753016 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -7.26068463107269 6.020739903442737 -7.093964197060433 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -7.665640024038328 6.186004740289944 -6.284173902929482 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -6.454379567105497 5.595183143274609 -6.803912718459241 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -5.922878937217112 -1.176560161323943 4.783431962107644 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -6.010351385330178 -0.2274127943903396 4.6517740197417 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -6.404180377155718 -1.34460019320307 5.649569719636831 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 7.846763062838132 -3.339353975130494 -0.008249014822193326 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 7.674994609488961 -4.121357481627367 -0.5467065412857492 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 7.951403236432504 -2.67112724115194 -0.6945812922055244 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -9.424856849133651 4.826765772230699 3.468218871054371 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -8.596505035353907 4.573349841331208 3.06416596817205 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 9.010643243367365 4.139309428954539 3.17847941634403 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -5.421086654925178 -5.019911752279892 6.759310816608537 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -5.649484325755156 -5.377982653023838 5.876409112119969 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -6.285643425156856 -4.956075965101634 7.278735663552695 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -2.756468999020262 -4.57641727193218 -8.707188682045459 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -1.798225567854454 -4.678306492629784 -8.931672388926 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -2.83486968898883 -5.342210573358408 -8.105794617638583 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 5.8157485820793 -3.67474795998444 5.011137590129627 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 5.711816897198752 -3.705012877013487 5.964200159059264 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 5.454565977411438 -4.507022420610661 4.625970703429743 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 3.692713883213812 -9.333860481209776 5.316526086688116 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 2.793322744037531 -9.160699208969662 5.719304009049557 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 3.949028102993074 -8.42967507307128 4.954834460087927 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 9.185977207388884 9.304926748004517 0.3815641888125099 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 8.964333208379282 -9.406649111487946 1.3033270028852 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 8.37854188872528 -9.39749230120845 -0.1409933303185325 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 2.34886348193929 -4.285575364214669 0.789917202287699 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 3.194663461703256 -4.517442567794069 1.207444437683103 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 2.363486380221229 -3.292148384568324 0.8875145660707269 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 6.04365170815042 -3.162568301853627 -4.355849565591759 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 5.13767861342012 -3.17587778891917 -4.837194849765588 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 6.328754883049268 -2.207696566373541 -4.197316086328198 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 5.2816123226462 7.549798211244064 -6.348587048254864 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 5.08217976139801 7.45787993994828 -5.390095121272243 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 5.396776440115968 8.505157449267017 -6.504649829417442 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -0.7097651694160213 -4.098758498067276 7.286840571397974 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 0.08231998337609807 -3.532442411612122 7.285764549251476 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -0.7064307859413168 -4.345402741040431 8.237457897248326 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -5.859259188039019 2.583715428517853 -4.476492010938948 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -5.489169381547335 1.667276099974243 -4.629587381410942 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -5.487041125742691 2.851055578099624 -3.638699609808485 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 8.526140105337237 6.238824215358282 0.04847115016332897 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 8.403171404614586 6.46227283957654 0.9766153187440866 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 9.199483308073816 5.597938305585354 0.1467107920511273 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 4.283930437328665 4.438293885043698 -2.579753419582167 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 4.223231354327531 5.229038169315294 -3.185007763299064 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 4.67815152183071 3.665296305918025 -3.117848130147603 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -5.748651965200443 3.068039069457559 -8.185299643010312 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -5.651616784214219 2.075935463519594 -8.330565701934209 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -6.649723152226231 3.207537606519704 -7.99139302796729 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -7.462415608571243 -4.186981495291648 -1.609256945209126 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -6.706220043541641 -4.617418360487492 -2.036947058123912 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -7.78509187269745 -3.62004551973407 -2.297633399939321 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -3.645740135013336 -0.6188784512558304 -6.8267967338453 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H -3.65006084612558 -1.582657219514521 -6.641225030576175 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -2.701230951810023 -0.4607511034404164 -6.871589431678858 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -8.893330463932609 -0.2827566150344867 -5.466110668474601 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 9.210494786855318 0.005453000206561006 -5.689783165720137 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H -8.669262855282769 -0.8987579452870503 -6.192554383699132 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 4.851600421354575 -0.8312924157951117 4.11702869658951 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 3.834864501482565 -0.9053649968635227 4.211044596235844 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 5.109098540906107 -1.750129193059416 4.399953301713772 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 6.793693258164818 -6.377018352909514 0.4770791291820219 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 6.447942594754008 -7.205370723909414 -0.002190320442521331 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 7.679414665362074 -6.281704271974585 0.1440862532617028 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O -9.555732394148423 -6.721974739783247 -9.359821812484547 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 9.143213480767441 -7.381629251593204 8.972308377625751 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 9.232871364951547 -7.13317688940793 -8.494656624677082 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        O 4.679840693494882 5.07710091370565 4.113939061994425 region=Builder ForceField.Type=OW ForceField.Charge=-0.834
        H 4.350974387536612 4.175264038660033 4.144315900935932 region=Builder ForceField.Type=HW ForceField.Charge=0.417
        H 4.214153994518096 5.516069064428178 4.843028092657009 region=Builder ForceField.Type=HW ForceField.Charge=0.417
    End
    Lattice
        19.0 0.0 0.0
        0.0 19.0 0.0
        0.0 0.0 19.0
    End
    BondOrders
         11 12 1.0
         11 13 1.0
         14 15 1.0
         14 16 1.0 0 -1 0
         17 18 1.0
         17 19 1.0
         20 21 1.0 0 -1 0
         20 22 1.0 0 -1 0
         23 24 1.0
         23 25 1.0
         26 27 1.0
         26 28 1.0
         29 30 1.0
         29 31 1.0
         32 33 1.0
         32 34 1.0
         35 36 1.0
         35 37 1.0
         38 39 1.0
         38 40 1.0 0 1 0
         41 42 1.0
         41 43 1.0
         44 45 1.0
         44 46 1.0
         47 48 1.0
         47 49 1.0
         50 51 1.0
         50 52 1.0
         53 54 1.0
         53 55 1.0
         56 57 1.0
         56 58 1.0
         59 60 1.0
         59 61 1.0
         62 63 1.0
         62 64 1.0
         65 66 1.0
         65 67 1.0
         68 69 1.0
         68 70 1.0
         71 72 1.0
         71 73 1.0
         74 75 1.0
         74 76 1.0
         77 78 1.0
         77 79 1.0
         80 81 1.0
         80 82 1.0
         83 84 1.0
         83 85 1.0
         86 87 1.0
         86 88 1.0
         89 90 1.0
         89 91 1.0 0 1 0
         92 93 1.0
         92 94 1.0 0 0 1
         95 96 1.0
         95 97 1.0
         98 99 1.0
         98 100 1.0
         101 102 1.0
         101 103 1.0
         104 105 1.0
         104 106 1.0
         107 108 1.0
         107 109 1.0
         110 111 1.0
         110 112 1.0 -1 0 0
         113 114 1.0
         113 115 1.0
         116 117 1.0
         116 118 1.0 0 0 -1
         119 120 1.0
         119 121 1.0
         122 123 1.0
         122 124 1.0
         125 126 1.0
         125 127 1.0 0 0 1
         128 129 1.0
         128 130 1.0
         131 132 1.0
         131 133 1.0
         134 135 1.0
         134 136 1.0
         137 138 1.0
         137 139 1.0
         140 141 1.0
         140 142 1.0
         143 144 1.0
         143 145 1.0
         146 147 1.0
         146 148 1.0
         149 150 1.0 1 0 0
         149 151 1.0 0 0 1
         152 153 1.0
         152 154 1.0
         155 156 1.0
         155 157 1.0
         158 159 1.0
         158 160 1.0
         161 162 1.0
         161 163 1.0
         164 165 1.0
         164 166 1.0
         167 168 1.0
         167 169 1.0
         170 171 1.0
         170 172 1.0
         173 174 1.0 0 -1 0
         173 175 1.0
         176 177 1.0
         176 178 1.0
         179 180 1.0
         179 181 1.0
         182 183 1.0
         182 184 1.0
         185 186 1.0
         185 187 1.0
         188 189 1.0
         188 190 1.0
         191 192 1.0
         191 193 1.0
         194 195 1.0
         194 196 1.0
         197 198 1.0
         197 199 1.0
         200 201 1.0
         200 202 1.0
         203 204 1.0
         203 205 1.0
         206 207 1.0 -1 0 0
         206 208 1.0 0 0 1
         209 210 1.0
         209 211 1.0
         212 213 1.0
         212 214 1.0
         215 216 1.0
         215 217 1.0
         218 219 1.0
         218 220 1.0
         221 222 1.0
         221 223 1.0
         224 225 1.0
         224 226 1.0
         227 228 1.0
         227 229 1.0
         230 231 1.0
         230 232 1.0
         233 234 1.0
         233 235 1.0
         236 237 1.0
         236 238 1.0
         239 240 1.0 1 0 0
         239 241 1.0 1 0 0
         242 243 1.0
         242 244 1.0
         245 246 1.0
         245 247 1.0
         248 249 1.0
         248 250 1.0
         251 252 1.0
         251 253 1.0
         254 255 1.0
         254 256 1.0
         257 258 1.0
         257 259 1.0
         260 261 1.0
         260 262 1.0
         263 264 1.0
         263 265 1.0
         266 267 1.0
         266 268 1.0
         269 270 1.0
         269 271 1.0
         272 273 1.0
         272 274 1.0
         275 276 1.0 1 0 0
         275 277 1.0
         278 279 1.0
         278 280 1.0 0 1 0
         281 282 1.0
         281 283 1.0
         284 285 1.0
         284 286 1.0
         287 288 1.0
         287 289 1.0
         290 291 1.0
         290 292 1.0
         293 294 1.0
         293 295 1.0
         296 297 1.0
         296 298 1.0
         299 300 1.0
         299 301 1.0
         302 303 1.0
         302 304 1.0
         305 306 1.0
         305 307 1.0
         308 309 1.0
         308 310 1.0
         311 312 1.0 -1 0 0
         311 313 1.0 -1 0 0
         314 315 1.0
         314 316 1.0
         317 318 1.0
         317 319 1.0
         320 321 1.0
         320 322 1.0
         323 324 1.0
         323 325 1.0
         326 327 1.0
         326 328 1.0
         329 330 1.0
         329 331 1.0
         332 333 1.0
         332 334 1.0
         335 336 1.0
         335 337 1.0
         338 339 1.0
         338 340 1.0
         341 342 1.0
         341 343 1.0
         344 345 1.0
         344 346 1.0
         347 348 1.0
         347 349 1.0
         350 351 1.0
         350 352 1.0
         353 354 1.0
         353 355 1.0
         356 357 1.0
         356 358 1.0
         359 360 1.0 0 0 -1
         359 361 1.0
         362 363 1.0
         362 364 1.0
         365 366 1.0
         365 367 1.0
         368 369 1.0
         368 370 1.0
         371 372 1.0
         371 373 1.0
         374 375 1.0
         374 376 1.0
         377 378 1.0
         377 379 1.0
         380 381 1.0
         380 382 1.0 0 0 -1
         383 384 1.0
         383 385 1.0
         386 387 1.0
         386 388 1.0
         389 390 1.0
         389 391 1.0
         392 393 1.0
         392 394 1.0
         395 396 1.0
         395 397 1.0
         398 399 1.0
         398 400 1.0
         401 402 1.0
         401 403 1.0
         404 405 1.0
         404 406 1.0
         407 408 1.0
         407 409 1.0
         410 411 1.0
         410 412 1.0
         413 414 1.0
         413 415 1.0
         416 417 1.0
         416 418 1.0
         419 420 1.0
         419 421 1.0
         422 423 1.0
         422 424 1.0
         425 426 1.0
         425 427 1.0
         428 429 1.0
         428 430 1.0
         431 432 1.0
         431 433 1.0
         434 435 1.0
         434 436 1.0
         437 438 1.0
         437 439 1.0 -1 0 0
         440 441 1.0
         440 442 1.0
         443 444 1.0
         443 445 1.0
         446 447 1.0
         446 448 1.0
         449 450 1.0
         449 451 1.0
         452 453 1.0
         452 454 1.0
         455 456 1.0
         455 457 1.0
         458 459 1.0
         458 460 1.0
         461 462 1.0
         461 463 1.0
         464 465 1.0
         464 466 1.0
         467 468 1.0
         467 469 1.0
         470 471 1.0
         470 472 1.0
         473 474 1.0
         473 475 1.0
         476 477 1.0
         476 478 1.0
         479 480 1.0
         479 481 1.0 0 0 1
         482 483 1.0
         482 484 1.0
         485 486 1.0
         485 487 1.0
         488 489 1.0
         488 490 1.0
         491 492 1.0
         491 493 1.0
         494 495 1.0
         494 496 1.0
         497 498 1.0
         497 499 1.0
         500 501 1.0
         500 502 1.0
         503 504 1.0
         503 505 1.0
         506 507 1.0
         506 508 1.0
         509 510 1.0
         509 511 1.0
         512 513 1.0
         512 514 1.0
         515 516 1.0
         515 517 1.0
         518 519 1.0
         518 520 1.0
         521 522 1.0
         521 523 1.0 0 0 -1
         524 525 1.0
         524 526 1.0
         527 528 1.0
         527 529 1.0
         530 531 1.0
         530 532 1.0
         533 534 1.0
         533 535 1.0
         536 537 1.0
         536 538 1.0
         539 540 1.0
         539 541 1.0
         542 543 1.0 1 0 0
         542 544 1.0
         545 546 1.0
         545 547 1.0
         548 549 1.0
         548 550 1.0 0 -1 0
         551 552 1.0
         551 553 1.0
         554 555 1.0
         554 556 1.0
         557 558 1.0
         557 559 1.0
         560 561 1.0
         560 562 1.0
         563 564 1.0 1 0 0
         563 565 1.0
         566 567 1.0
         566 568 1.0
         569 570 1.0
         569 571 1.0
         572 573 1.0
         572 574 1.0
         575 576 1.0
         575 577 1.0
         578 579 1.0 -1 0 0
         578 580 1.0
         581 582 1.0
         581 583 1.0
         584 585 1.0
         584 586 1.0
         587 588 1.0
         587 589 1.0
         590 591 1.0
         590 592 1.0
         593 594 1.0
         593 595 1.0
         596 597 1.0
         596 598 1.0
         599 600 1.0
         599 601 1.0
         602 603 1.0
         602 604 1.0
         605 606 1.0
         605 607 1.0
         608 609 1.0
         608 610 1.0 -1 0 0
         611 612 1.0
         611 613 1.0
         614 615 1.0
         614 616 1.0
         617 618 1.0
         617 619 1.0
         620 621 1.0
         620 622 1.0
         623 624 1.0 0 1 0
         623 625 1.0 0 1 0
         626 627 1.0
         626 628 1.0
         629 630 1.0
         629 631 1.0
         632 633 1.0
         632 634 1.0
         635 636 1.0
         635 637 1.0
         638 639 1.0
         638 640 1.0
         641 642 1.0
         641 643 1.0
         644 645 1.0
         644 646 1.0
         647 648 1.0
         647 649 1.0
         650 651 1.0
         650 652 1.0
         653 654 1.0
         653 655 1.0
         656 657 1.0 -1 0 0
         656 658 1.0
         659 660 1.0
         659 661 1.0
         662 663 1.0
         662 664 1.0
         665 666 1.0 -1 0 -1
         665 667 1.0 -1 0 0
         668 669 1.0
         668 670 1.0
    End
End"""
    main(text)
