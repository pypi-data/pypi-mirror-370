import SimpleITK as sitk
import numpy as np
pi = np.pi
__AUTHOR__ = 'Bahram Jafrasteh'
"""
Image to image registration using Simple ITK package (it is under development)
"""

def command_multi_iteration(method):
    print("--------- Resolution Changing ---------")


def command_iteration(method):
    print(
        f"{method.GetOptimizerIteration():3} "
        + f"= {method.GetMetricValue():10.5f} "
        + f": {method.GetOptimizerPosition()}"
    )


def command_multiresolution_iteration(method):
    print(f"\tStop Condition: {method.GetOptimizerStopConditionDescription()}")
    print("============= Resolution Change =============")

def RegistrationSpline(fixed, moving, criterion, *params):
    criterion = criterion.lower()
    R = sitk.ImageRegistrationMethod()
    params = params[0]
    fixed_mask = params['fixed_mask']
    fixed_points = params['fixed_points']
    moving_points = params['moving_points']
    MultiRes = params['MultiRes']
    numberOfBins = params['nbins']
    transformDomainMeshSize = [10] * moving.GetDimension()
    tx = sitk.BSplineTransformInitializer(fixed, transformDomainMeshSize)

    print("Initial Parameters:")
    print(tx.GetParameters())

    R = sitk.ImageRegistrationMethod()
    if criterion not in ['mi', 'correlation', 'jmi']:
        criterion = 'mi'
        print('setting criterion as mutual information')
    if criterion=='mi':
        R.SetMetricAsMattesMutualInformation(numberOfBins)
        R.SetOptimizerAsGradientDescentLineSearch(
        5.0, 100, convergenceMinimumValue=1e-4, convergenceWindowSize=5
        )
    elif criterion=='correlation':
        R.SetMetricAsCorrelation()

        R.SetOptimizerAsLBFGSB(
            gradientConvergenceTolerance=1e-5,
            numberOfIterations=100,
            maximumNumberOfCorrections=5,
            maximumNumberOfFunctionEvaluations=1000,
            costFunctionConvergenceFactor=1e7,
        )
    elif criterion=='jmi':
        R.SetMetricAsJointHistogramMutualInformation()

        R.SetOptimizerAsGradientDescentLineSearch(
            5.0, 100, convergenceMinimumValue=1e-4, convergenceWindowSize=5
        )
    R.SetOptimizerScalesFromPhysicalShift()
    R.SetInitialTransform(tx)
    R.SetInterpolator(sitk.sitkLinear)
    if MultiRes:
        R.SetShrinkFactorsPerLevel([6, 2, 1])
        R.SetSmoothingSigmasPerLevel([6, 2, 1])

    R.AddCommand(
        sitk.sitkMultiResolutionIterationEvent, lambda: command_multi_iteration(R)
    )
    return run_registration(R, fixed, moving)


def RegistrationRigid(fixed, moving, criterion, *params):
    R = sitk.ImageRegistrationMethod()
    params = params[0]
    fixed_mask = params['fixed_mask']
    fixed_points = params['fixed_points']
    moving_points = params['moving_points']
    MultiRes = params['MultiRes']
    numberOfBins = params['nbins']
    transform = sitk.CenteredTransformInitializer(
        fixed,
        moving,
        sitk.Euler3DTransform(),
        sitk.CenteredTransformInitializerFilter.GEOMETRY,
    )
    if criterion.lower()=='mse':
        R.SetMetricAsMeanSquares()
    elif criterion.lower()=='correlation':
        R.SetMetricAsCorrelation()
    elif criterion.lower()=='mi':
        R.SetMetricAsMattesMutualInformation(numberOfBins)
    elif criterion.lower()=='jmi':
        R.SetMetricAsJointHistogramMutualInformation(numberOfBins)
    R.SetInitialTransform(sitk.TranslationTransform(fixed.GetDimension()))
    R.SetMetricSamplingStrategy(R.NONE)
    R.SetInterpolator(sitk.sitkLinear)
    R.SetOptimizerAsGradientDescent(
        learningRate=1.0,
        numberOfIterations=300,
        convergenceMinimumValue=1e-6,
        convergenceWindowSize=10,
    )
    R.SetOptimizerScalesFromPhysicalShift()
    R.SetInitialTransform(transform, inPlace=True)
    R.SetInterpolator(sitk.sitkLinear)
    if MultiRes:
        R.SetShrinkFactorsPerLevel([6,2, 1])
        R.SetSmoothingSigmasPerLevel([6,2, 1])
    return run_registration(R, fixed, moving)

def registartion1(file_ref, file_target, method='mse', normalized=False, *params):
    #https://github.com/nvladimus/ITK_sandbox
    import SimpleITK as sitk
    import sys
    import os


    fixed = sitk.ReadImage(file_ref, sitk.sitkFloat32)

    moving = sitk.ReadImage(file_target, sitk.sitkFloat32)

    if normalized:
        fixed = sitk.Normalize(fixed)
        fixed = sitk.DiscreteGaussian(fixed, 2.0)
        moving = sitk.Normalize(moving)
        moving = sitk.DiscreteGaussian(moving, 2.0)
    R = sitk.ImageRegistrationMethod()

    if method=='rigid':
        transform = sitk.CenteredTransformInitializer(
            fixed,
            moving,
            sitk.Euler3DTransform(),
            sitk.CenteredTransformInitializerFilter.GEOMETRY,
        )

        R.SetMetricAsCorrelation()
        R.SetMetricSamplingStrategy(R.NONE)
        R.SetInterpolator(sitk.sitkLinear)
        R.SetOptimizerAsGradientDescent(
            learningRate=1.0,
            numberOfIterations=300,
            convergenceMinimumValue=1e-6,
            convergenceWindowSize=10,
        )
        R.SetOptimizerScalesFromPhysicalShift()
        R.SetInitialTransform(transform, inPlace=True)
        #R.SetOptimizerWeights([0, 0, 1, 1, 1, 1]) # to allow rotate only on z axis


    if method=='mse':

        R.SetMetricAsMeanSquares()
        R.SetOptimizerAsRegularStepGradientDescent(4.0, 0.01, 200)
        R.SetInitialTransform(sitk.TranslationTransform(fixed.GetDimension()))
        R.SetInterpolator(sitk.sitkLinear)
    elif method == 'HMI':
        R.SetMetricAsJointHistogramMutualInformation()

        R.SetOptimizerAsGradientDescentLineSearch(
            learningRate=1.0,
            numberOfIterations=200,
            convergenceMinimumValue=1e-5,
            convergenceWindowSize=5,
        )
        R.SetInitialTransform(sitk.TranslationTransform(fixed.GetDimension()))
        R.SetInterpolator(sitk.sitkLinear)
    elif method=='CC':
        R.SetMetricAsCorrelation()

        R.SetOptimizerAsRegularStepGradientDescent(
            learningRate=2.0,
            minStep=1e-4,
            numberOfIterations=500,
            gradientMagnitudeTolerance=1e-8,
        )
        R.SetOptimizerScalesFromIndexShift()

        tx = sitk.CenteredTransformInitializer(
            fixed, moving, sitk.Similarity2DTransform()
        )
        R.SetInitialTransform(tx)

        R.SetInterpolator(sitk.sitkLinear)
    elif method=='MI':
        numberOfBins = params[0]['nbins']
        samplingPercentage = params[0]['sp']
        R.SetMetricAsMattesMutualInformation(numberOfBins)
        R.SetMetricSamplingPercentage(samplingPercentage, sitk.sitkWallClock)
        R.SetMetricSamplingStrategy(R.RANDOM)
        R.SetOptimizerAsRegularStepGradientDescent(1.0, 0.001, 500)
        R.SetInitialTransform(sitk.TranslationTransform(fixed.GetDimension()))
        R.SetInterpolator(sitk.sitkLinear)
    elif method=='BsplineCC':
        transformDomainMeshSize = [8] * moving.GetDimension()
        tx = sitk.BSplineTransformInitializer(fixed, transformDomainMeshSize)

        print("Initial Parameters:")
        print(tx.GetParameters())

        R = sitk.ImageRegistrationMethod()
        R.SetMetricAsCorrelation()

        R.SetOptimizerAsLBFGSB(
            gradientConvergenceTolerance=1e-5,
            numberOfIterations=100,
            maximumNumberOfCorrections=5,
            maximumNumberOfFunctionEvaluations=1000,
            costFunctionConvergenceFactor=1e7,
        )
        R.SetInitialTransform(tx, True)
        R.SetInterpolator(sitk.sitkLinear)
    elif method=='BsplineMI':
        transformDomainMeshSize = [10] * moving.GetDimension()
        tx = sitk.BSplineTransformInitializer(fixed, transformDomainMeshSize)

        print("Initial Parameters:")
        print(tx.GetParameters())

        R = sitk.ImageRegistrationMethod()
        R.SetMetricAsMattesMutualInformation(50)
        R.SetOptimizerAsGradientDescentLineSearch(
            5.0, 100, convergenceMinimumValue=1e-4, convergenceWindowSize=5
        )
        R.SetOptimizerScalesFromPhysicalShift()
        R.SetInitialTransform(tx)
        R.SetInterpolator(sitk.sitkLinear)

        R.SetShrinkFactorsPerLevel([6, 2, 1])
        R.SetSmoothingSigmasPerLevel([6, 2, 1])

        R.AddCommand(
            sitk.sitkMultiResolutionIterationEvent, lambda: command_multi_iteration(R)
        )
    elif method=='BsplineHMI':
        transformDomainMeshSize = [2] * fixed.GetDimension()
        tx = sitk.BSplineTransformInitializer(fixed, transformDomainMeshSize)

        print(f"Initial Number of Parameters: {tx.GetNumberOfParameters()}")

        R = sitk.ImageRegistrationMethod()
        R.SetMetricAsJointHistogramMutualInformation()

        R.SetOptimizerAsGradientDescentLineSearch(
            5.0, 100, convergenceMinimumValue=1e-4, convergenceWindowSize=5
        )

        R.SetInterpolator(sitk.sitkLinear)

        R.SetInitialTransformAsBSpline(tx, inPlace=True, scaleFactors=[1, 2, 5])
        R.SetShrinkFactorsPerLevel([4, 2, 1])
        R.SetSmoothingSigmasPerLevel([4, 2, 1])
        R.AddCommand(
            sitk.sitkMultiResolutionIterationEvent, lambda: command_multi_iteration(R)
        )
    elif method=='displacement':

        initialTx = sitk.CenteredTransformInitializer(
            fixed, moving, sitk.AffineTransform(fixed.GetDimension())
        )

        R = sitk.ImageRegistrationMethod()

        R.SetShrinkFactorsPerLevel([3, 2, 1])
        R.SetSmoothingSigmasPerLevel([2, 1, 1])

        R.SetMetricAsJointHistogramMutualInformation(20)
        R.MetricUseFixedImageGradientFilterOff()

        R.SetOptimizerAsGradientDescent(
            learningRate=1.0,
            numberOfIterations=100,
            estimateLearningRate=R.EachIteration,
        )
        R.SetOptimizerScalesFromPhysicalShift()

        R.SetInitialTransform(initialTx)

        R.SetInterpolator(sitk.sitkLinear)

        R.AddCommand(sitk.sitkIterationEvent, lambda: command_iteration(R))
        R.AddCommand(
            sitk.sitkMultiResolutionIterationEvent,
            lambda: command_multiresolution_iteration(R),
        )

        outTx1 = R.Execute(fixed, moving)

        print("-------")
        print(outTx1)
        print(f"Optimizer stop condition: {R.GetOptimizerStopConditionDescription()}")
        print(f" Iteration: {R.GetOptimizerIteration()}")
        print(f" Metric value: {R.GetMetricValue()}")

        displacementField = sitk.Image(fixed.GetSize(), sitk.sitkVectorFloat64)
        displacementField.CopyInformation(fixed)
        displacementTx = sitk.DisplacementFieldTransform(displacementField)
        del displacementField
        displacementTx.SetSmoothingGaussianOnUpdate(
            varianceForUpdateField=0.0, varianceForTotalField=1.5
        )

        R.SetMovingInitialTransform(outTx1)
        R.SetInitialTransform(displacementTx, inPlace=True)

        R.SetMetricAsANTSNeighborhoodCorrelation(4)
        R.MetricUseFixedImageGradientFilterOff()

        R.SetShrinkFactorsPerLevel([3, 2, 1])
        R.SetSmoothingSigmasPerLevel([2, 1, 1])

        R.SetOptimizerScalesFromPhysicalShift()
        R.SetOptimizerAsGradientDescent(
            learningRate=1,
            numberOfIterations=300,
            estimateLearningRate=R.EachIteration,
        )

        R.Execute(fixed, moving)

        print("-------")
        print(displacementTx)
        print(f"Optimizer stop condition: {R.GetOptimizerStopConditionDescription()}")
        print(f" Iteration: {R.GetOptimizerIteration()}")
        print(f" Metric value: {R.GetMetricValue()}")

        compositeTx = sitk.CompositeTransform([outTx1, displacementTx])


        if "SITK_NOSHOW" not in os.environ:
            sitk.Show(displacementTx.GetDisplacementField(), "Displacement Field")

            resampler = sitk.ResampleImageFilter()
            resampler.SetReferenceImage(fixed)
            resampler.SetInterpolator(sitk.sitkLinear)
            resampler.SetDefaultPixelValue(100)
            resampler.SetTransform(compositeTx)

            out = resampler.Execute(moving)
            return out
    elif method=='Exhaustive':
        R = sitk.ImageRegistrationMethod()

        R.SetMetricAsMattesMutualInformation(numberOfHistogramBins=50)

        sample_per_axis = 12
        if fixed.GetDimension() == 2:
            tx = sitk.Euler2DTransform()
            # Set the number of samples (radius) in each dimension, with a
            # default step size of 1.0
            R.SetOptimizerAsExhaustive([sample_per_axis // 2, 0, 0])
            # Utilize the scale to set the step size for each dimension
            R.SetOptimizerScales([2.0 * pi / sample_per_axis, 1.0, 1.0])
        elif fixed.GetDimension() == 3:
            tx = sitk.Euler3DTransform()
            R.SetOptimizerAsExhaustive(
                [
                    sample_per_axis // 2,
                    sample_per_axis // 2,
                    sample_per_axis // 4,
                    0,
                    0,
                    0,
                ]
            )
            R.SetOptimizerScales(
                [
                    2.0 * pi / sample_per_axis,
                    2.0 * pi / sample_per_axis,
                    2.0 * pi / sample_per_axis,
                    1.0,
                    1.0,
                    1.0,
                ]
            )

        # Initialize the transform with a translation and the center of
        # rotation from the moments of intensity.
        tx = sitk.CenteredTransformInitializer(fixed, moving, tx)

        R.SetInitialTransform(tx)

        R.SetInterpolator(sitk.sitkLinear)


    return run_registration(R, fixed, moving)

def run_registration(R, fixed, moving):
    R.AddCommand(sitk.sitkIterationEvent, lambda: command_iteration(R))

    outTx = R.Execute(fixed, moving)

    print("-------")
    print(outTx)
    print(f"Optimizer stop condition: {R.GetOptimizerStopConditionDescription()}")
    print(f" Iteration: {R.GetOptimizerIteration()}")
    print(f" Metric value: {R.GetMetricValue()}")

    resampler = sitk.ResampleImageFilter()
    resampler.SetReferenceImage(fixed)
    resampler.SetInterpolator(sitk.sitkLinear)
    resampler.SetDefaultPixelValue(0)
    resampler.SetTransform(outTx)
    out = resampler.Execute(moving)
    return out, outTx

def apply_reg(outTx, fixed, moving):
    resampler = sitk.ResampleImageFilter()
    resampler.SetReferenceImage(fixed)
    resampler.SetInterpolator(sitk.sitkNearestNeighbor)
    resampler.SetDefaultPixelValue(0)
    resampler.SetTransform(outTx)
    out = resampler.Execute(moving)
    return out

def FFD_registration(fixed, moving, criterion='mse', *params):
    R = sitk.ImageRegistrationMethod()
    params = params[0]
    fixed_mask = params['fixed_mask']
    fixed_points = params['fixed_points']
    moving_points = params['moving_points']
    MultiRes = params['MultiRes']
    numberOfBins = params['nbins']
    # Determine the number of BSpline control points using the physical spacing we
    # want for the finest resolution control grid.
    grid_physical_spacing = [50.0, 50.0, 50.0]  # A control point every 50mm
    image_physical_size = [
        size * spacing
        for size, spacing in zip(fixed.GetSize(), fixed.GetSpacing())
    ]
    mesh_size = [
        int(image_size / grid_spacing + 0.5)
        for image_size, grid_spacing in zip(image_physical_size, grid_physical_spacing)
    ]

    # The starting mesh size will be 1/4 of the original, it will be refined by
    # the multi-resolution framework.
    mesh_size = [int(sz / 4 + 0.5) for sz in mesh_size]

    initial_transform = sitk.BSplineTransformInitializer(
        image1=fixed, transformDomainMeshSize=mesh_size, order=3
    )
    # Instead of the standard SetInitialTransform we use the BSpline specific method which also
    # accepts the scaleFactors parameter to refine the BSpline mesh. In this case we start with
    # the given mesh_size at the highest pyramid level then we double it in the next lower level and
    # in the full resolution image we use a mesh that is four times the original size.
    if MultiRes:
        R.SetInitialTransformAsBSpline(
        initial_transform, inPlace=True, scaleFactors=[1, 2, 4]
        )
    else:
        R.SetInitialTransform(initial_transform)
    if criterion.lower()=='mse':
        R.SetMetricAsMeanSquares()
    elif criterion.lower()=='correlation':
        R.SetMetricAsCorrelation()
    elif criterion.lower()=='mi':
        R.SetMetricAsMattesMutualInformation(numberOfBins)

    # Settings for metric sampling, usage of a mask is optional. When given a mask the sample points will be
    # generated inside that region. Also, this implicitly speeds things up as the mask is smaller than the
    # whole image.
    R.SetMetricSamplingStrategy(R.RANDOM)
    samplingPercentage = params['sp']#0.01
    R.SetMetricSamplingPercentage(samplingPercentage)
    if fixed_mask:
        R.SetMetricFixedMask(fixed_mask)

    # Multi-resolution framework.
    R.SetShrinkFactorsPerLevel(shrinkFactors=[4, 2, 1])
    R.SetSmoothingSigmasPerLevel(smoothingSigmas=[2, 1, 0])
    R.SmoothingSigmasAreSpecifiedInPhysicalUnitsOn()

    R.SetInterpolator(sitk.sitkLinear)
    if MultiRes:
        # Use the LBFGS2 instead of LBFGS. The latter cannot adapt to the changing control grid resolution.
        R.SetOptimizerAsLBFGS2(
            solutionAccuracy=1e-2, numberOfIterations=100, deltaConvergenceTolerance=0.01
        )
    else:
        R.SetOptimizerAsLBFGSB(
            gradientConvergenceTolerance=1e-5,
            numberOfIterations=100,
            maximumNumberOfCorrections=5,
            maximumNumberOfFunctionEvaluations=1000,
            costFunctionConvergenceFactor=1e7,
        )

    # If corresponding points in the fixed and moving image are given then we display the similarity metric
    # and the TRE during the registration.
    if fixed_points and moving_points:
        import registration_callbacks as rc
        R.AddCommand(
            sitk.sitkStartEvent, rc.metric_and_reference_start_plot
        )
        R.AddCommand(
            sitk.sitkEndEvent, rc.metric_and_reference_end_plot
        )
        R.AddCommand(
            sitk.sitkIterationEvent,
            lambda: rc.metric_and_reference_plot_values(
                R, fixed_points, moving_points
            ),
        )

    return run_registration(R, fixed, moving)